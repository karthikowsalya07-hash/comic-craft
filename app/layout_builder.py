from typing import List
from .models import ComicStory, ComicPanel


def build_comic_layout(story: ComicStory, image_paths: List[str]) -> List[ComicPanel]:
    """
    Validate and assemble the comic layout.
    Enforces that exactly 5 panels exist, and every panel has exactly one corresponding image.
    """
    if len(story.panels) != 5:
        raise ValueError(f"Comic must contain exactly 5 panels; received {len(story.panels)}.")

    if len(image_paths) != 5:
        raise ValueError(f"Comic requires exactly 5 images; received {len(image_paths)}.")

    if len(story.panels) != len(image_paths):
        raise ValueError("Every story panel must have exactly one corresponding generated image.")

    layout: List[ComicPanel] = []
    for panel, image_path in zip(story.panels, image_paths):
        if not image_path:
            raise ValueError(f"Panel {panel.panel_number} is missing an image path.")

        layout.append(
            ComicPanel(
                panel_number=panel.panel_number,
                title=panel.title,
                image_path=image_path,
                scene_description=panel.scene_description,
                caption=panel.caption,
                narration=panel.narration,
                dialogue=panel.dialogue,
                image_prompt=panel.image_prompt,
            )
        )
    return layout
