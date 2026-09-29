from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft - AI Comic Story Creator"
    gemini_api_key: str = ""
    hf_token: str = ""
    # Gemini model defaults:
    gemini_outline_model: str = "gemini-flash-lite-latest"
    gemini_story_model: str = "gemini-flash-lite-latest"
    gemini_fallback_models: list[str] = [
        "gemini-flash-lite-latest",
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-flash-latest",
    ]
    # Hugging Face text-to-image defaults:
    hf_image_model: str = "stabilityai/stable-diffusion-3-medium-diffusers"
    hf_provider: str = "hf-inference"
    hf_fallback_models: list[str] = [
        "stabilityai/stable-diffusion-3-medium-diffusers",
        "black-forest-labs/FLUX.1-schnell",
        "ByteDance/SDXL-Lightning",
    ]
    image_width: int = 768
    image_height: int = 1024
    image_steps: int = 28
    
    # Absolute paths:
    output_dir: Path = BASE_DIR / "static"
    panels_dir: Path = BASE_DIR / "static" / "panels"
    exports_dir: Path = BASE_DIR / "static" / "exports"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.panels_dir.mkdir(parents=True, exist_ok=True)
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    return settings
