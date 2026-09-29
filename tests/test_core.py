import pytest
from pathlib import Path
from app.layout_builder import build_comic_layout
from app.models import ComicStory, PanelStory, ComicPanel
from app.exporters import save_pdf, _resolve_image_path
from app.image_generator import generate_image


def _create_mock_story(panel_count: int = 5) -> ComicStory:
    panels = []
    for i in range(1, panel_count + 1):
        panels.append(
            PanelStory(
                panel_number=i,
                title=f"Panel {i} Title",
                scene_description=f"Action in panel {i}",
                caption=f"Caption for panel {i}",
                narration=f"Narration for panel {i}",
                dialogue=f"Dialogue {i}" if i % 2 == 0 else "",
                image_prompt=f"Comic book hero in scene {i}",
            )
        )
    return ComicStory(panels=panels)


def test_layout_builder_validates_five_panels():
    # Valid 5 panels with 5 images
    story = _create_mock_story(5)
    image_paths = [f"/static/panels/panel_{i}.png" for i in range(1, 6)]
    layout = build_comic_layout(story, image_paths)
    
    assert len(layout) == 5
    for idx, panel in enumerate(layout, 1):
        assert panel.panel_number == idx
        assert panel.image_path == f"/static/panels/panel_{idx}.png"


def test_layout_builder_rejects_non_five_panels():
    # Only 4 panels
    story = _create_mock_story(4)
    image_paths = [f"/static/panels/panel_{i}.png" for i in range(1, 5)]
    with pytest.raises(ValueError, match="Comic must contain exactly 5 panels"):
        build_comic_layout(story, image_paths)


def test_layout_builder_rejects_mismatched_images():
    # 5 panels but 4 images
    story = _create_mock_story(5)
    image_paths = [f"/static/panels/panel_{i}.png" for i in range(1, 5)]
    with pytest.raises(ValueError, match="Comic requires exactly 5 images"):
        build_comic_layout(story, image_paths)


def test_pdf_export_and_path_resolution(tmp_path):
    story = _create_mock_story(5)
    
    # Generate resilient local placeholder images for all 5 panels
    image_paths = [generate_image(f"Test prompt {i}", i) for i in range(1, 6)]
    assert len(image_paths) == 5
    for p in image_paths:
        assert p.startswith("/static/panels/")

    layout = build_comic_layout(story, image_paths)
    pdf_filename = save_pdf(layout, title="Test Comic Book")
    
    assert pdf_filename.endswith(".pdf")
    from app.config import get_settings
    settings = get_settings()
    pdf_file = settings.exports_dir / pdf_filename
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 1000
