import logging
from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .config import BASE_DIR, get_settings
from .exporters import save_pdf
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .jobs import create_job, get_job
from .layout_builder import build_comic_layout
from .models import GenerateResponse, JobStartResponse, JobStatusResponse, PromptRequest

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ---------------------------------------------------------------------------
# Core synchronous pipeline (unchanged — used by legacy endpoints and jobs)
# ---------------------------------------------------------------------------

def _generate_comic(data: PromptRequest):
    """
    Synchronous five-step pipeline.
    Called by /generate-comic/json (legacy JSON endpoint) and preserved for
    any code that needs the synchronous path.
    The background job worker (jobs.py) re-implements the same steps with
    progress hooks — this function stays untouched for backward compatibility.
    """
    logger.info("Starting comic generation for character '%s'", data.character_name)

    outline = generate_outline(
        data.story_prompt,
        data.character_name,
        data.setting,
        data.tone,
        data.art_style,
    )

    story = generate_story(outline, data.character_name, data.tone)

    image_paths = [
        generate_image(panel.image_prompt, panel.panel_number)
        for panel in story.panels
    ]

    layout = build_comic_layout(story, image_paths)

    pdf_filename = save_pdf(
        layout,
        title=f"ComicCraft - {data.character_name}'s Comic",
    )
    return layout, pdf_filename


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"error": None},
    )


@router.get("/comic/{comic_id}", response_class=HTMLResponse)
async def comic_detail(request: Request, comic_id: str):
    """
    Render a completed comic by its comic_id (PDF filename stem).
    This page is navigated to by the frontend after polling completes.
    """
    settings = get_settings()
    pdf_filename = f"{comic_id}.pdf"
    pdf_path = settings.exports_dir / pdf_filename

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Comic not found.")

    return templates.TemplateResponse(
        request=request,
        name="comic_ready.html",
        context={
            "comic_id": comic_id,
            "pdf_filename": pdf_filename,
            "pdf_url": f"/download/{pdf_filename}",
        },
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )


# ---------------------------------------------------------------------------
# Background generation (new async path)
# ---------------------------------------------------------------------------

@router.post("/generate", response_class=JSONResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    """
    Start a background comic-generation job.

    Returns JSON immediately with the job_id.
    The client polls GET /api/jobs/{job_id} for progress.
    On completion the response includes comic_id which can be opened at
    GET /comic/{comic_id}.
    """
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
    except Exception as exc:
        # Validation error — return JSON so the JS polling code can handle it
        return JSONResponse(
            status_code=422,
            content={"success": False, "error": str(exc)},
        )

    job_id = create_job(_generate_comic, data)
    logger.info("Background job created: %s for character '%s'", job_id, character_name)

    return JSONResponse(
        status_code=202,
        content=JobStartResponse(job_id=job_id, status="queued").model_dump(),
    )


# ---------------------------------------------------------------------------
# Job status API
# ---------------------------------------------------------------------------

@router.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
async def job_status(job_id: str):
    """
    GET /api/jobs/{job_id}

    Poll this endpoint to track progress of a background generation job.

    Response fields
    ---------------
    job_id      str           Unique identifier for this job
    status      str           queued | generating | saving | completed | failed
    progress    int           0–100 completion percentage
    message     str           Human-readable current step description
    comic_id    str | null    Set when status == completed; use with /comic/{comic_id}
    pdf_url     str | null    Direct PDF download URL (set when completed)
    error       str | null    Error detail (set when status == failed)
    """
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    pdf_url: str | None = None
    if job.status == "completed" and job.pdf_filename:
        pdf_url = f"/download/{job.pdf_filename}"

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        comic_id=job.comic_id,
        pdf_url=pdf_url,
        error=job.error,
    )


# ---------------------------------------------------------------------------
# Legacy / utility endpoints (preserved unchanged)
# ---------------------------------------------------------------------------

@router.post("/generate-comic/json", response_model=GenerateResponse)
async def generate_json(data: PromptRequest):
    """
    Synchronous JSON API endpoint (legacy, preserved for backward compatibility).
    Blocks until the full pipeline completes.
    """
    try:
        layout, pdf_filename = _generate_comic(data)
        return GenerateResponse(
            success=True,
            panels=layout,
            pdf_url=f"/download/{pdf_filename}",
            pdf_filename=pdf_filename,
        )
    except Exception as exc:
        logger.error("JSON comic generation failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/test-image")
async def test_image(
    prompt: str = "A brave fox exploring an enchanted forest, comic illustration",
):
    try:
        path = generate_image(prompt, 0)
        return {"success": True, "image_url": path}
    except Exception as exc:
        logger.error("Test image generation failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/download/{filename}")
async def download(filename: str):
    settings = get_settings()
    requested = (settings.exports_dir / filename).resolve()

    if requested.parent != settings.exports_dir.resolve():
        raise HTTPException(status_code=400, detail="Invalid filename.")

    if not requested.exists() or requested.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found.")

    return FileResponse(
        path=requested,
        media_type="application/pdf",
        filename=requested.name,
    )
