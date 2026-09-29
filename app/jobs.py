"""
Background job system for ComicCraft.

Architecture
------------
Jobs are stored in an in-process dict protected by a threading.Lock.
Each comic-generation request:
  1. Creates a JobRecord with a unique UUID.
  2. Spawns a daemon Thread that runs _generate_comic_job().
  3. Returns the job_id immediately to the caller.

The daemon thread updates the JobRecord at real pipeline milestones
(queued → generating → panel images → saving → exporting → completed/failed).

Thread safety
-------------
All reads and writes to _JOBS go through _JOBS_LOCK.  Individual JobRecord
fields are Python built-ins (str, int, float, None) which are updated atomically
on CPython, but we always hold the lock around compound reads/writes to keep the
implementation safe even under alternative Python runtimes.

Lifecycle states
----------------
  queued      – job created, thread not yet scheduled
  generating  – outline + story generation in progress
  saving      – layout assembled, PDF being written
  completed   – all done; comic_id / pdf_filename available
  failed      – unrecoverable error; error field populated
"""

from __future__ import annotations

import logging
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Job record
# ---------------------------------------------------------------------------

@dataclass
class JobRecord:
    """Holds the state of a single background generation job."""

    job_id: str
    status: str = "queued"           # queued | generating | saving | completed | failed
    progress: int = 0                # 0–100
    message: str = "Queued, waiting to start…"
    comic_id: Optional[str] = None   # set on completion (same as pdf_filename stem)
    pdf_filename: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# In-process job store
# ---------------------------------------------------------------------------

_JOBS: dict[str, JobRecord] = {}
_JOBS_LOCK = threading.Lock()


def _update_job(job_id: str, **kwargs: Any) -> None:
    """Thread-safe partial update of a JobRecord."""
    with _JOBS_LOCK:
        rec = _JOBS.get(job_id)
        if rec is None:
            return
        for key, value in kwargs.items():
            setattr(rec, key, value)


def get_job(job_id: str) -> Optional[JobRecord]:
    """Return a *copy* of the JobRecord so callers can read fields safely."""
    with _JOBS_LOCK:
        rec = _JOBS.get(job_id)
        if rec is None:
            return None
        # Return a shallow copy so the caller sees a consistent snapshot
        return JobRecord(
            job_id=rec.job_id,
            status=rec.status,
            progress=rec.progress,
            message=rec.message,
            comic_id=rec.comic_id,
            pdf_filename=rec.pdf_filename,
            error=rec.error,
        )


def list_jobs() -> list[JobRecord]:
    """Return copies of all jobs (useful for introspection / tests)."""
    with _JOBS_LOCK:
        return [
            JobRecord(
                job_id=r.job_id,
                status=r.status,
                progress=r.progress,
                message=r.message,
                comic_id=r.comic_id,
                pdf_filename=r.pdf_filename,
                error=r.error,
            )
            for r in _JOBS.values()
        ]


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

def _generate_comic_job(
    job_id: str,
    generate_fn: Callable,   # the _generate_comic() function from routes.py
    data: Any,               # PromptRequest instance
) -> None:
    """
    Worker function executed in a daemon thread.

    Progress milestones (aligned with the real pipeline):
      0  %  – queued / created
      5  %  – thread started, preparing
      15 %  – calling Gemini for story outline
      35 %  – calling Gemini for story script
      40 %  – starting panel image generation (5 images)
      40–75% – image generation progress (8 % per panel × 5 = +40 %)
               Each panel: 40 + (i * 8) where i = 0..4
      75 %  – all images done, building layout
      80 %  – saving / exporting PDF
      90 %  – PDF saved
      100 % – completed
    """
    logger.info("[job:%s] Worker thread started for character '%s'", job_id, getattr(data, "character_name", "?"))

    try:
        # ---- 5 % : thread running ----
        _update_job(job_id,
                    status="generating",
                    progress=5,
                    message="Preparing generation pipeline…")

        # We need fine-grained progress hooks inside _generate_comic().
        # Rather than passing the opaque function and losing visibility,
        # we replicate the pipeline steps here with explicit progress updates.
        # This keeps the existing _generate_comic() intact for synchronous use
        # while giving us per-step hooks here.

        from .config import get_settings          # noqa: PLC0415
        from .exporters import save_pdf           # noqa: PLC0415
        from .gemini_flash import generate_outline  # noqa: PLC0415
        from .gemini_pro import generate_story    # noqa: PLC0415
        from .image_generator import generate_image  # noqa: PLC0415
        from .layout_builder import build_comic_layout  # noqa: PLC0415

        # ---- 15 % : outline ----
        _update_job(job_id,
                    progress=15,
                    message="Generating five-panel story outline with Gemini…")

        outline = generate_outline(
            data.story_prompt,
            data.character_name,
            data.setting,
            data.tone,
            data.art_style,
        )

        # ---- 35 % : story script ----
        _update_job(job_id,
                    progress=35,
                    message="Expanding outline into full comic script…")

        story = generate_story(outline, data.character_name, data.tone)

        # ---- 40–75 % : panel images (8 % each) ----
        image_paths: list[str] = []
        for idx, panel in enumerate(story.panels):
            pct = 40 + idx * 7  # 40, 47, 54, 61, 68
            _update_job(job_id,
                        progress=pct,
                        message=f"Generating panel {panel.panel_number} illustration ({idx + 1}/5)…")
            path = generate_image(panel.image_prompt, panel.panel_number)
            image_paths.append(path)

        # ---- 75 % : layout assembly ----
        _update_job(job_id,
                    progress=75,
                    message="Assembling comic layout…")

        layout = build_comic_layout(story, image_paths)

        # ---- 80 % : PDF export ----
        _update_job(job_id,
                    status="saving",
                    progress=80,
                    message="Exporting comic to PDF…")

        pdf_filename = save_pdf(
            layout,
            title=f"ComicCraft - {data.character_name}'s Comic",
        )

        # ---- 90 % : finalising ----
        _update_job(job_id,
                    progress=90,
                    message="Finalising PDF…")

        # comic_id = the PDF stem (without extension), used as a stable identifier
        comic_id = pdf_filename.replace(".pdf", "")

        # ---- 100 % : completed ----
        _update_job(job_id,
                    status="completed",
                    progress=100,
                    message="Comic generation complete!",
                    comic_id=comic_id,
                    pdf_filename=pdf_filename)

        logger.info("[job:%s] Completed successfully. PDF: %s", job_id, pdf_filename)

    except Exception as exc:
        logger.error("[job:%s] Failed: %s", job_id, exc, exc_info=True)
        _update_job(job_id,
                    status="failed",
                    progress=0,
                    message="Generation failed.",
                    error=str(exc))


# ---------------------------------------------------------------------------
# Public API: create a job
# ---------------------------------------------------------------------------

def create_job(generate_fn: Callable, data: Any) -> str:
    """
    Create a new background generation job.

    Returns the job_id immediately.  The actual generation runs in a daemon
    thread so the HTTP request can return without blocking.

    Parameters
    ----------
    generate_fn : callable
        The _generate_comic function (passed in to avoid a circular import).
        Not actually called directly — kept for API symmetry and potential
        future use (e.g. swapping in a mock during tests).
    data : PromptRequest
        The validated comic generation parameters.
    """
    job_id = str(uuid.uuid4())

    record = JobRecord(
        job_id=job_id,
        status="queued",
        progress=0,
        message="Queued, waiting to start…",
    )

    with _JOBS_LOCK:
        _JOBS[job_id] = record

    thread = threading.Thread(
        target=_generate_comic_job,
        args=(job_id, generate_fn, data),
        name=f"comiccraft-job-{job_id[:8]}",
        daemon=True,   # thread won't block app shutdown
    )
    thread.start()

    logger.info("[job:%s] Created and thread started.", job_id)
    return job_id
