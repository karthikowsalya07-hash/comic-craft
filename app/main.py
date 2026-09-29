from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routes import router


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Generate five-panel AI comics with Gemini and Hugging Face image generation.",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=str(settings.output_dir)),
    name="static",
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ComicCraft"}
