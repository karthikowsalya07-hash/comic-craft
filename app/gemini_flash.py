from .config import get_settings
from .gemini_client import generate_structured
from .models import ComicOutline


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> ComicOutline:
    settings = get_settings()
    prompt = f"""
Create a coherent five-panel comic outline.

User story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Requirements:
- Return exactly 5 panels.
- Keep the same main character and setting throughout.
- Give each panel a concise title.
- scene_description should explain what happens visually.
- image_prompt should be a detailed prompt for a text-to-image model.
- The image prompt must describe the character consistently and include the requested art style.
- Do not include copyrighted characters, living artists' names, logos, or trademarks.
- Make the story family-friendly and visually clear.
"""
    outline = generate_structured(settings.gemini_outline_model, prompt, ComicOutline)
    if len(outline.panels) != 5:
        raise RuntimeError(f"Gemini returned {len(outline.panels)} panels instead of 5.")
    return outline
