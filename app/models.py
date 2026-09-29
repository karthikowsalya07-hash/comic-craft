from typing import List
from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=3, max_length=2000)
    character_name: str = Field(..., min_length=1, max_length=80)
    setting: str = Field(..., min_length=1, max_length=120)
    tone: str = Field(..., min_length=1, max_length=60)
    art_style: str = Field(..., min_length=1, max_length=80)


class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: List[PanelOutline]


class PanelStory(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str = ""
    image_prompt: str


class ComicStory(BaseModel):
    panels: List[PanelStory]


class ComicPanel(BaseModel):
    panel_number: int
    title: str
    image_path: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str


class GenerateResponse(BaseModel):
    success: bool
    panels: List[ComicPanel]
    pdf_url: str
    pdf_filename: str


# ---------------------------------------------------------------------------
# Background job models
# ---------------------------------------------------------------------------

class JobStartResponse(BaseModel):
    """Returned immediately when POST /generate accepts the job."""
    job_id: str
    status: str = "queued"


class JobStatusResponse(BaseModel):
    """Returned by GET /api/jobs/{job_id}."""
    job_id: str
    status: str          # queued | generating | saving | completed | failed
    progress: int        # 0–100
    message: str
    comic_id: str | None = None   # set when completed
    pdf_url: str | None = None    # set when completed
    error: str | None = None      # set when failed
