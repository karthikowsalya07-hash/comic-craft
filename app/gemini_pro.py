from .config import get_settings
from .gemini_client import generate_structured
from .models import ComicOutline, ComicStory


def generate_story(
    outline: ComicOutline,
    character_name: str,
    tone: str,
) -> ComicStory:
    settings = get_settings()
    outline_json = outline.model_dump_json(indent=2)
    prompt = f"""
Expand this five-panel comic outline into a polished comic script.

Main character: {character_name}
Tone: {tone}

Outline:
{outline_json}

Requirements:
- Return exactly the same five panel numbers.
- Preserve each panel title, scene description, and image prompt unless a small
  consistency improvement is needed.
- Add a short caption, narration, and optional dialogue for every panel.
- Keep narration concise enough to fit on a comic page.
- Dialogue must be natural and age-appropriate.
- Maintain continuity from panel to panel.
- Do not use copyrighted characters or imitate a living artist.
"""
    story = generate_structured(settings.gemini_story_model, prompt, ComicStory)
    if len(story.panels) != 5:
        raise RuntimeError(f"Gemini returned {len(story.panels)} story panels instead of 5.")
    return story
