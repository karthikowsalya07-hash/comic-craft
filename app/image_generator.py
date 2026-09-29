from datetime import datetime
import logging
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont

from huggingface_hub import InferenceClient

from .config import get_settings

logger = logging.getLogger(__name__)


def _safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-")
    return value[:50] or "panel"


def _create_placeholder_image(output_path: Path, panel_number: int, prompt_summary: str, reason: str = ""):
    """Generate a clean comic-styled placeholder image if HF inference is unavailable."""
    width, height = 768, 1024
    image = Image.new("RGB", (width, height), color="#2b2d42")
    draw = ImageDraw.Draw(image)

    # Decorative comic frame border
    border_margin = 24
    draw.rectangle(
        [(border_margin, border_margin), (width - border_margin, height - border_margin)],
        outline="#edf2f4",
        width=4,
    )
    draw.rectangle(
        [(border_margin + 8, border_margin + 8), (width - border_margin - 8, height - border_margin - 8)],
        outline="#8d99ae",
        width=2,
    )

    # Header badge
    badge_w, badge_h = 320, 64
    badge_x0 = (width - badge_w) // 2
    badge_y0 = 80
    draw.rectangle(
        [(badge_x0, badge_y0), (badge_x0 + badge_w, badge_y0 + badge_h)],
        fill="#ef233c",
        outline="#edf2f4",
        width=2,
    )

    badge_text = f"PANEL {panel_number}"
    draw.text((badge_x0 + 80, badge_y0 + 16), badge_text, fill="#ffffff")

    # Center illustration box
    center_y = height // 2 - 60
    draw.rectangle(
        [(80, 220), (width - 80, height - 220)],
        fill="#1e1f29",
        outline="#8d99ae",
        width=2,
    )

    # Comic icon art inside box
    draw.ellipse([(width // 2 - 70, center_y - 120), (width // 2 + 70, center_y + 20)], outline="#d90429", width=4)
    draw.text((width // 2 - 130, center_y + 40), "COMIC ILLUSTRATION", fill="#edf2f4")
    
    # Prompt text wrap / snippet
    wrapped_lines = []
    words = prompt_summary.split()
    current_line = []
    for word in words:
        current_line.append(word)
        if len(" ".join(current_line)) > 36:
            wrapped_lines.append(" ".join(current_line))
            current_line = []
        if len(wrapped_lines) >= 4:
            break
    if current_line and len(wrapped_lines) < 4:
        wrapped_lines.append(" ".join(current_line))

    text_y = center_y + 90
    for line in wrapped_lines:
        draw.text((100, text_y), line, fill="#8d99ae")
        text_y += 28

    if reason:
        draw.text((100, height - 160), f"Note: {reason[:70]}", fill="#e0a96d")

    image.save(output_path, "PNG")


def generate_image(image_prompt: str, panel_number: int) -> str:
    """
    Generate panel image using Hugging Face hosted inference client.
    If HF_TOKEN is not configured or inference fails, gracefully falls back to a 
    clean branded comic panel illustration so the user's comic workflow and PDF export never break.
    """
    settings = get_settings()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"panel_{panel_number}_{timestamp}_{_safe_name(image_prompt)}.png"
    output_path = settings.panels_dir / filename

    if not settings.hf_token or settings.hf_token.strip() in ("", "your_huggingface_token_here"):
        logger.warning("HF_TOKEN is not configured; creating fallback panel image.")
        _create_placeholder_image(
            output_path,
            panel_number=panel_number,
            prompt_summary=image_prompt,
            reason="HF_TOKEN not configured in .env",
        )
        return f"/static/panels/{filename}"

    full_prompt = (
        f"{image_prompt}. Clean comic illustration, strong readable composition, "
        "consistent character design, expressive faces, no text, no watermark."
    )

    models_to_try = [settings.hf_image_model]
    for fallback in settings.hf_fallback_models:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_hf_err = ""
    for model_name in models_to_try:
        try:
            logger.info("Attempting HF image inference with model: %s for panel %d", model_name, panel_number)
            client = InferenceClient(
                provider=settings.hf_provider,
                api_key=settings.hf_token.strip(),
            )
            image = client.text_to_image(
                prompt=full_prompt,
                model=model_name,
                width=settings.image_width,
                height=settings.image_height,
                num_inference_steps=settings.image_steps,
            )
            image.save(output_path, "PNG")
            return f"/static/panels/{filename}"
        except Exception as exc:
            last_hf_err = str(exc)
            logger.warning("HF image inference failed with model %s: %s", model_name, exc)
            continue

    # Graceful fallback: create high quality placeholder illustration so PDF and preview never crash
    logger.warning("All HF image inference models failed. Creating resilient comic panel placeholder.")
    _create_placeholder_image(
        output_path,
        panel_number=panel_number,
        prompt_summary=image_prompt,
        reason=f"HF Inference unavailable ({last_hf_err[:50]})",
    )
    return f"/static/panels/{filename}"
