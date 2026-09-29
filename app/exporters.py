from datetime import datetime
import logging
from pathlib import Path
from fpdf import FPDF
from PIL import Image

from .config import get_settings
from .models import ComicPanel

logger = logging.getLogger(__name__)


def _safe_text(value: str) -> str:
    # Built-in PDF fonts are not Unicode-complete. Keep the export robust.
    return value.encode("latin-1", "replace").decode("latin-1")


def _resolve_image_path(image_path_str: str) -> Path:
    """
    Safely resolve image path across platforms (Windows / Linux / macOS).
    Handles relative web routes like '/static/panels/xyz.png' or direct file paths.
    """
    settings = get_settings()
    raw = image_path_str.strip()
    
    # If path starts with /static/ or static/
    clean_relative = raw.lstrip("/").replace("\\", "/")
    if clean_relative.startswith("static/"):
        relative_to_static = clean_relative[len("static/"):]
        candidate = settings.output_dir / relative_to_static
        if candidate.exists():
            return candidate.resolve()

    # Direct filename in panels dir
    panel_candidate = settings.panels_dir / Path(raw).name
    if panel_candidate.exists():
        return panel_candidate.resolve()

    # Direct path
    direct_path = Path(raw)
    if direct_path.exists():
        return direct_path.resolve()

    # Output dir parent
    parent_candidate = settings.output_dir.parent / clean_relative
    if parent_candidate.exists():
        return parent_candidate.resolve()

    return panel_candidate.resolve()


def save_pdf(layout: list[ComicPanel], title: str = "ComicCraft Comic") -> str:
    """
    Compile comic layout into a beautiful multi-page PDF document.
    Ensures Windows-compatible image paths and strict FPDF2 cell boundaries.
    """
    settings = get_settings()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comiccraft_{timestamp}.pdf"
    output_path = settings.exports_dir / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_title(_safe_text(title))

        # Title
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, _safe_text(f"Panel {panel.panel_number}: {panel.title}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Robust image path resolution for Windows and Unix
        image_file = _resolve_image_path(panel.image_path)
        if not image_file.exists():
            logger.warning("Image file %s does not exist for PDF. Creating emergency panel image.", image_file)
            image_file.parent.mkdir(parents=True, exist_ok=True)
            fallback_img = Image.new("RGB", (768, 1024), color="#333333")
            fallback_img.save(image_file, "PNG")

        # Place image on page: A4 width is 210mm, margin 15mm on each side leaves 180mm max
        img_w = 160
        img_x = (210 - img_w) / 2
        pdf.image(str(image_file.resolve()), x=img_x, y=30, w=img_w)
        
        # Position below image (30 + 115 = 145mm)
        pdf.set_xy(15, 148)

        # Story description and narration
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 5, _safe_text(panel.scene_description), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, _safe_text("Caption"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, _safe_text(panel.caption), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, _safe_text("Narration"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, _safe_text(panel.narration), new_x="LMARGIN", new_y="NEXT")

        if panel.dialogue and panel.dialogue.strip():
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, _safe_text("Dialogue"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, _safe_text(f'"{panel.dialogue.strip()}"'), new_x="LMARGIN", new_y="NEXT")

    pdf.output(str(output_path.resolve()))
    return filename
