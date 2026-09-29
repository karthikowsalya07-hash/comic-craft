"""
ComicCraft PowerPoint Presentation Generator
Generates a 20-slide academic presentation using python-pptx.
Run from the ComicCraft project root directory.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import sys


# ─── Colour Palette ───────────────────────────────────────────────────────────
DARK_BG     = RGBColor(0x1A, 0x1A, 0x2E)   # deep navy background
ACCENT      = RGBColor(0xE9, 0x4F, 0x37)   # vivid red-orange accent
ACCENT2     = RGBColor(0x39, 0x3E, 0x46)   # dark grey panel
TITLE_WHITE = RGBColor(0xFF, 0xFF, 0xFF)   # white text
BODY_LIGHT  = RGBColor(0xD4, 0xD4, 0xD4)   # light grey body text
HIGHLIGHT   = RGBColor(0xF5, 0xA6, 0x23)   # golden yellow highlight
SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


def _set_bg(slide, color: RGBColor):
    """Fill slide background with a solid colour."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_textbox(slide, text, left, top, width, height,
                 font_size=18, bold=False, color=TITLE_WHITE,
                 align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox


def _add_accent_bar(slide, top=Inches(1.15), height=Inches(0.06)):
    """Thin horizontal accent bar below title."""
    bar = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(0.4), top, Inches(12.53), height
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()


def _add_slide_number(slide, num):
    _add_textbox(slide, str(num),
                 Inches(12.5), Inches(7.0), Inches(0.6), Inches(0.35),
                 font_size=11, color=RGBColor(0x88, 0x88, 0x88),
                 align=PP_ALIGN.RIGHT)


def _title_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    _set_bg(slide, DARK_BG)

    # Decorative top bar
    bar = slide.shapes.add_shape(1, 0, 0, SLIDE_W, Inches(0.18))
    bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT; bar.line.fill.background()

    # Project title
    _add_textbox(slide,
                 "ComicCraft",
                 Inches(0.6), Inches(1.4), Inches(12.1), Inches(1.2),
                 font_size=54, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    _add_textbox(slide,
                 "AI Comic Story Creator",
                 Inches(0.6), Inches(2.5), Inches(12.1), Inches(0.7),
                 font_size=30, bold=False, color=TITLE_WHITE, align=PP_ALIGN.CENTER)

    # Subtitle tagline
    _add_textbox(slide,
                 "Transforming a text idea into a five-panel illustrated comic\n"
                 "using Google Gemini and Hugging Face",
                 Inches(1.2), Inches(3.3), Inches(10.9), Inches(0.9),
                 font_size=17, italic=True, color=BODY_LIGHT, align=PP_ALIGN.CENTER)

    # Tech stack strip
    _add_textbox(slide,
                 "Python  ·  FastAPI  ·  Google Gemini  ·  Hugging Face  ·  FPDF2  ·  Pydantic",
                 Inches(0.6), Inches(4.4), Inches(12.1), Inches(0.5),
                 font_size=14, color=HIGHLIGHT, align=PP_ALIGN.CENTER)

    # Bottom bar
    bar2 = slide.shapes.add_shape(1, 0, Inches(7.32), SLIDE_W, Inches(0.18))
    bar2.fill.solid(); bar2.fill.fore_color.rgb = ACCENT; bar2.line.fill.background()

    _add_textbox(slide, "1", Inches(12.5), Inches(7.0), Inches(0.6), Inches(0.35),
                 font_size=11, color=RGBColor(0x88, 0x88, 0x88), align=PP_ALIGN.RIGHT)


def _content_slide(prs, slide_num: int, title: str, bullets: list[str],
                   subtitle: str = ""):
    """Standard content slide: dark bg, accent bar, title, bullet list."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, DARK_BG)

    # Slide title
    _add_textbox(slide, title,
                 Inches(0.4), Inches(0.18), Inches(12.1), Inches(0.85),
                 font_size=28, bold=True, color=TITLE_WHITE)

    _add_accent_bar(slide, top=Inches(1.02), height=Inches(0.05))

    if subtitle:
        _add_textbox(slide, subtitle,
                     Inches(0.4), Inches(1.12), Inches(12.1), Inches(0.4),
                     font_size=14, italic=True, color=HIGHLIGHT)

    # Bullet content
    content_top = Inches(1.55) if subtitle else Inches(1.18)
    content_h = Inches(5.6) if subtitle else Inches(5.8)

    txBox = slide.shapes.add_textbox(Inches(0.5), content_top, Inches(12.1), content_h)
    tf = txBox.text_frame
    tf.word_wrap = True

    for i, bullet in enumerate(bullets):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()

        # Section headers (lines ending with ':' or starting with '##')
        if bullet.startswith("##"):
            p.space_before = Pt(10)
            run = p.add_run()
            run.text = bullet[2:].strip()
            run.font.size = Pt(15)
            run.font.bold = True
            run.font.color.rgb = ACCENT
        elif bullet.endswith(":") and len(bullet) < 50:
            p.space_before = Pt(8)
            run = p.add_run()
            run.text = bullet
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = HIGHLIGHT
        elif bullet.startswith("  "):
            p.level = 1
            run = p.add_run()
            run.text = "  • " + bullet.strip()
            run.font.size = Pt(13)
            run.font.color.rgb = BODY_LIGHT
        elif bullet == "":
            run = p.add_run()
            run.text = ""
            run.font.size = Pt(8)
        else:
            run = p.add_run()
            run.text = "▸  " + bullet
            run.font.size = Pt(14)
            run.font.color.rgb = TITLE_WHITE

    _add_slide_number(slide, slide_num)


def _two_col_slide(prs, slide_num, title, left_items, right_items,
                   left_head="", right_head=""):
    """Two-column layout slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, DARK_BG)

    _add_textbox(slide, title,
                 Inches(0.4), Inches(0.18), Inches(12.1), Inches(0.85),
                 font_size=28, bold=True, color=TITLE_WHITE)
    _add_accent_bar(slide, top=Inches(1.02), height=Inches(0.05))

    col_w = Inches(6.0)
    col_top = Inches(1.15)
    col_h = Inches(6.0)

    for col_idx, (head, items, left) in enumerate(
        [(left_head, left_items, Inches(0.4)),
         (right_head, right_items, Inches(6.9))]
    ):
        if head:
            _add_textbox(slide, head, left, col_top, col_w, Inches(0.45),
                         font_size=15, bold=True, color=HIGHLIGHT)
            body_top = col_top + Inches(0.48)
        else:
            body_top = col_top

        txBox = slide.shapes.add_textbox(left, body_top, col_w, col_h)
        tf = txBox.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            if item == "":
                run = p.add_run(); run.text = ""; run.font.size = Pt(7)
            elif item.startswith("##"):
                run = p.add_run(); run.text = item[2:].strip()
                run.font.size = Pt(13); run.font.bold = True
                run.font.color.rgb = ACCENT
            else:
                run = p.add_run()
                run.text = "▸  " + item
                run.font.size = Pt(13); run.font.color.rgb = TITLE_WHITE

    _add_slide_number(slide, slide_num)


def build_presentation(output_path: str):
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    # ── Slide 1: Title ──────────────────────────────────────────────────────
    _title_slide(prs)

    # ── Slide 2: Introduction ───────────────────────────────────────────────
    _content_slide(prs, 2, "Introduction", [
        "ComicCraft is a web-based Generative AI application",
        "Converts a plain text story idea into a five-panel illustrated comic book",
        "",
        "User provides five inputs:",
        "  Story idea (text prompt)",
        "  Main character name",
        "  Setting",
        "  Tone  (e.g. Adventurous, Funny, Dramatic)",
        "  Art style  (e.g. Comic Book, Watercolor, Manga)",
        "",
        "System automatically produces:",
        "  A structured five-panel narrative (caption, narration, dialogue)",
        "  One AI-generated illustration per panel",
        "  A downloadable A4 PDF comic book",
    ])

    # ── Slide 3: Problem Statement ──────────────────────────────────────────
    _two_col_slide(prs, 3, "Problem Statement",
        left_head="Creating a Comic Requires:",
        left_items=[
            "Strong narrative writing skills",
            "Illustration / digital art expertise",
            "Panel layout & composition knowledge",
            "Access to professional software",
            "",
            "Result: High barrier to entry",
            "Most people have a story idea but",
            "lack the skills to execute it",
        ],
        right_head="Existing Tools Are Incomplete:",
        right_items=[
            "ChatGPT → text only, no images, no PDF",
            "DALL·E / Midjourney → images only",
            "Canva / Pixton → clip-art, no AI story",
            "Local Stable Diffusion → requires GPU",
            "",
            "No tool provides an end-to-end pipeline:",
            "Text idea → Story → Images → Layout → PDF",
        ]
    )

    # ── Slide 4: Existing System ────────────────────────────────────────────
    _content_slide(prs, 4, "Existing System — Analysis", [
        "ChatGPT / LLMs → story text only; no images, no layout, no PDF",
        "DALL·E / Midjourney → images only; no narrative, no multi-panel structure",
        "Canva Comics → pre-made clip-art; no AI story or image generation",
        "Pixton → fixed characters; no AI text or image generation",
        "Adobe Express → graphic templates; no AI story or image pipeline",
        "Local Stable Diffusion → high-quality images but requires GPU; no story or PDF",
        "",
        "Core gap identified:",
        "  No tool provides a complete automated pipeline from",
        "  a plain text idea to a finished illustrated exportable comic",
        "  without requiring artistic skill or specialised hardware",
    ])

    # ── Slide 5: Proposed System ────────────────────────────────────────────
    _content_slide(prs, 5, "Proposed System — ComicCraft", [
        "End-to-end pipeline: Text prompt → Story → Images → Preview → PDF",
        "",
        "Key design principles:",
        "  Structured AI output  — Gemini returns typed JSON matched to Pydantic schemas",
        "  Multi-tier fallback   — Gemini and HF both have automatic model fallback chains",
        "  Strict validation     — exactly 5 panels and 5 images enforced at every stage",
        "  Security              — path traversal protection; API keys never in responses",
        "  Accessibility         — no artistic or writing skill required from the user",
        "",
        "Pipeline:",
        "  User prompt → Gemini outline → Gemini script → HF images → Layout → HTML + PDF",
    ])

    # ── Slide 6: Objectives ─────────────────────────────────────────────────
    _content_slide(prs, 6, "Project Objectives", [
        "Story Generation   — 5-panel outline and full script via Google Gemini",
        "Image Generation   — one AI illustration per panel via Hugging Face inference",
        "5-Panel Validation — exactly 5 panels + 5 images enforced at every stage",
        "Comic Preview      — HTML preview rendered immediately after generation",
        "PDF Export         — downloadable A4 PDF comic book via FPDF2",
        "Resilience         — pipeline always completes; graceful fallback at every layer",
        "API Documentation  — auto-generated Swagger UI at /docs",
        "Security           — Pydantic input validation; filename path-traversal protection",
    ])

    # ── Slide 7: System Architecture ───────────────────────────────────────
    _content_slide(prs, 7, "System Architecture", [
        "Linear pipeline with validation checkpoints at each stage",
        "",
        "Step 1  →  User input validated by Pydantic PromptRequest",
        "Step 2  →  gemini_flash.py  →  Google Gemini API",
        "            Returns: ComicOutline  (5 × PanelOutline)",
        "Step 3  →  gemini_pro.py    →  Google Gemini API",
        "            Returns: ComicStory   (5 × PanelStory)",
        "Step 4  →  image_generator.py  →  Hugging Face InferenceClient × 5",
        "            Fallback: Pillow placeholder PNG",
        "Step 5  →  layout_builder.py   →  Validates 5 panels + 5 images",
        "            Returns: List[ComicPanel]",
        "Step 6  →  exporters.py  →  FPDF2  →  A4 PDF saved to static/exports/",
        "Step 7  →  Jinja2 renders comic_preview.html → browser",
    ])

    # ── Slide 8: Technologies Used ──────────────────────────────────────────
    _two_col_slide(prs, 8, "Technologies Used",
        left_head="Backend",
        left_items=[
            "Python 3.10+       — core language",
            "FastAPI            — web framework, routing, docs",
            "Uvicorn            — ASGI server",
            "Jinja2             — server-side HTML templates",
            "Pydantic v2        — data models, validation",
            "pydantic-settings  — .env configuration",
            "google-genai       — Gemini API client",
            "huggingface-hub    — HF InferenceClient",
            "FPDF2              — PDF generation",
            "Pillow             — fallback image creation",
        ],
        right_head="Frontend & Testing",
        right_items=[
            "HTML / CSS / JS    — form, preview, loading state",
            "python-dotenv      — .env loading",
            "python-multipart   — HTML form parsing",
            "pytest             — test framework",
            "httpx              — HTTP client",
            "",
            "##Key versions",
            "FastAPI  ≥ 0.115",
            "Pydantic ≥ 2.8",
            "google-genai ≥ 1.30",
            "FPDF2    ≥ 2.8",
        ]
    )

    # ── Slide 9: Module Description ─────────────────────────────────────────
    _two_col_slide(prs, 9, "Module Description",
        left_head="Core Modules",
        left_items=[
            "config.py       — settings, .env, output dirs",
            "models.py       — all Pydantic data schemas",
            "routes.py       — all HTTP endpoints",
            "gemini_client.py — Gemini API, fallback chain",
            "gemini_flash.py — outline generation",
            "gemini_pro.py   — script expansion",
        ],
        right_head="Pipeline Modules",
        right_items=[
            "image_generator.py — HF inference + fallback",
            "layout_builder.py  — 5-panel validation + assembly",
            "exporters.py       — FPDF2 PDF + path resolution",
            "main.py            — app factory, static mount",
            "",
            "##Data flow",
            "models.py schemas connect all modules",
            "config.py settings used by every module",
        ]
    )

    # ── Slide 10: AI Workflow ───────────────────────────────────────────────
    _content_slide(prs, 10, "AI Workflow — Two-Stage Gemini Pipeline",
        subtitle="Gemini structured JSON output mode — no text parsing required",
        bullets=[
        "##Stage 1 — Outline  (gemini_flash.py)",
        "Input: story_prompt, character_name, setting, tone, art_style",
        "Output: ComicOutline — 5 × PanelOutline",
        "  Each panel: panel_number, title, scene_description, image_prompt",
        "Validation: RuntimeError if panel count ≠ 5",
        "",
        "##Stage 2 — Script Expansion  (gemini_pro.py)",
        "Input: ComicOutline JSON + character_name + tone",
        "Output: ComicStory — 5 × PanelStory",
        "  Adds: caption, narration, dialogue to each panel",
        "Validation: RuntimeError if panel count ≠ 5",
        "",
        "Both stages use: response_mime_type='application/json'  +  response_schema=<PydanticModel>",
    ])

    # ── Slide 11: Backend Implementation ────────────────────────────────────
    _two_col_slide(prs, 11, "Backend Implementation",
        left_head="HTTP Endpoints",
        left_items=[
            "GET  /               Home page — story form",
            "POST /generate       Form → comic_preview.html",
            "POST /generate-comic/json  JSON API",
            "GET  /download/{fn}  PDF download (secure)",
            "GET  /test-image     HF image test",
            "GET  /health         Liveness check",
            "GET  /docs           Swagger UI (auto-generated)",
        ],
        right_head="Input Validation (Pydantic)",
        right_items=[
            "story_prompt    3–2000 characters",
            "character_name  1–80 characters",
            "setting         1–120 characters",
            "tone            1–60 characters",
            "art_style       1–80 characters",
            "",
            "Validation errors → index.html with message",
            "Pipeline errors   → index.html with message",
            "JSON API errors   → HTTPException(500)",
        ]
    )

    # ── Slide 12: Frontend Implementation ───────────────────────────────────
    _content_slide(prs, 12, "Frontend Implementation", [
        "Three Jinja2 HTML templates — all rendering is server-side",
        "",
        "index.html:",
        "  Story input form with 5 fields",
        "  Client-side validation (empty field detection)",
        "  Loading spinner activated on submit",
        "  Inline error messages if generation fails",
        "",
        "comic_preview.html:",
        "  Renders all 5 ComicPanel objects in a card layout",
        "  Each card: title → image → caption → narration → dialogue",
        "  Download PDF button → /download/<filename>",
        "",
        "Styling (static/css/style.css):",
        "  Dark comic aesthetic; animated loading states; responsive layout",
        "  No JavaScript framework — plain HTML, CSS, vanilla JS",
    ])

    # ── Slide 13: Gemini Integration ─────────────────────────────────────────
    _content_slide(prs, 13, "Gemini Integration",
        subtitle="gemini_client.py — structured output with automatic model fallback",
        bullets=[
        "Client created with GEMINI_API_KEY; raises RuntimeError if key is absent",
        "generate_structured() calls client.models.generate_content() with:",
        "  response_mime_type = 'application/json'",
        "  response_schema    = <Pydantic model class>",
        "Response parsed via response.parsed or schema.model_validate_json(text)",
        "",
        "Fallback chain (tried in order if primary model fails):",
        "  gemini-flash-lite-latest  →  gemini-3.8-flash  →  gemini-3.5-flash",
        "  →  gemini-3.1-flash-lite  →  gemini-flash-latest",
        "",
        "Error classification:",
        "  404 / NOT_FOUND           → try next model",
        "  429 / RESOURCE_EXHAUSTED  → try next model",
        "  503 / UNAVAILABLE         → try next model",
        "  401 / 403 / INVALID KEY   → raise immediately (fallback won't help)",
    ])

    # ── Slide 14: Hugging Face Image Generation ─────────────────────────────
    _content_slide(prs, 14, "Hugging Face Image Generation",
        subtitle="image_generator.py — two-tier fallback ensures pipeline always completes",
        bullets=[
        "InferenceClient.text_to_image() called once per panel (5 calls total)",
        "Image dimensions: 768 × 1024 px  |  Inference steps: 28",
        "",
        "Primary model: stabilityai/stable-diffusion-3-medium-diffusers",
        "Fallbacks: black-forest-labs/FLUX.1-schnell  →  ByteDance/SDXL-Lightning",
        "",
        "Tier 1 fallback: HF_TOKEN absent or placeholder → skip HF entirely",
        "Tier 2 fallback: any HF model failure → try next model in list",
        "Final fallback:  all HF models fail → Pillow placeholder image",
        "",
        "Pillow placeholder maintains comic aesthetic:",
        "  Dark background, double comic frame, red PANEL N badge,",
        "  prompt summary text, note explaining why placeholder was used",
    ])

    # ── Slide 15: Five-Panel Layout & PDF Generation ─────────────────────────
    _two_col_slide(prs, 15, "Layout Builder & PDF Generation",
        left_head="layout_builder.py",
        left_items=[
            "Validates: len(story.panels) == 5",
            "Validates: len(image_paths) == 5",
            "Validates: panels count == image count",
            "Assembles List[ComicPanel] by zipping",
            "story panels with image paths",
            "",
            "Raises ValueError with clear message",
            "if any validation fails",
        ],
        right_head="exporters.py (FPDF2)",
        right_items=[
            "A4 portrait, one page per panel",
            "Panel title  — Helvetica Bold 18pt",
            "Panel image  — 160mm wide, centred",
            "Scene desc.  — Helvetica Italic 10pt",
            "Caption      — label + body text",
            "Narration    — label + body text",
            "Dialogue     — label + body (if non-empty)",
            "",
            "Path resolver handles Win/Unix differences",
            "Emergency fallback image if file missing",
        ]
    )

    # ── Slide 16: Error Handling & Fallbacks ────────────────────────────────
    _two_col_slide(prs, 16, "Error Handling & Fallback Behavior",
        left_head="Gemini API Errors",
        left_items=[
            "404 NOT_FOUND      → try next model",
            "429 QUOTA EXCEEDED → try next model",
            "503 UNAVAILABLE    → try next model",
            "401/403 INVALID KEY → raise immediately",
            "All models fail    → RuntimeError",
            "",
            "Security:",
            "API keys validated before first call",
            "Placeholder key rejected with clear error",
        ],
        right_head="Image & Request Errors",
        right_items=[
            "HF_TOKEN missing   → Pillow placeholder",
            "HF model fails     → try next HF model",
            "All HF models fail → Pillow placeholder",
            "Image missing at PDF time → grey image",
            "",
            "Request validation:",
            "Pydantic validates before any API call",
            "Errors → index.html with message",
            "",
            "Download security:",
            "Path traversal attempt → HTTP 400",
            "File not found → HTTP 404",
        ]
    )

    # ── Slide 17: Testing ────────────────────────────────────────────────────
    _content_slide(prs, 17, "Testing",
        subtitle="4 automated tests — all pass offline without API credentials",
        bullets=[
        "test_layout_builder_validates_five_panels",
        "  5 panels + 5 images → correct List[ComicPanel] with matching numbers and paths",
        "",
        "test_layout_builder_rejects_non_five_panels",
        "  4 panels → ValueError: 'Comic must contain exactly 5 panels'",
        "",
        "test_layout_builder_rejects_mismatched_images",
        "  5 panels + 4 images → ValueError: 'Comic requires exactly 5 images'",
        "",
        "test_pdf_export_and_path_resolution",
        "  Generates 5 placeholder images → builds layout → saves PDF",
        "  Asserts: file exists on disk; file size > 1000 bytes",
        "",
        "Result:  4 passed in 0.64s   (pytest -v)",
        "Coverage: layout builder, image fallback, PDF generation, path resolution",
    ])

    # ── Slide 18: Results ────────────────────────────────────────────────────
    _content_slide(prs, 18, "Results", [
        "Google Gemini story outline generation         — Implemented and working",
        "Gemini script expansion (caption/narration)    — Implemented and working",
        "Hugging Face text-to-image generation          — Working (requires HF_TOKEN)",
        "Fallback placeholder image generation          — Always available (no token needed)",
        "Strict 5-panel + 5-image validation            — Enforced at 4 pipeline stages",
        "HTML comic preview                             — Implemented and working",
        "A4 PDF export with per-panel images and text   — Implemented and working",
        "Swagger UI auto-documentation at /docs         — Available",
        "JSON REST API endpoint                         — POST /generate-comic/json",
        "Path traversal protection on downloads         — Implemented",
        "Automated test suite                           — 4 / 4 tests passing",
    ])

    # ── Slide 19: Limitations & Future Enhancements ─────────────────────────
    _two_col_slide(prs, 19, "Limitations & Future Enhancements",
        left_head="Current Limitations",
        left_items=[
            "Fixed 5-panel output only",
            "HF free tier: strict rate limits (30–90s)",
            "PDF font encoding: latin-1 only",
            "No session or user history",
            "No content moderation layer",
            "HTTP request blocks during generation",
            "Relies on Gemini structured JSON output",
        ],
        right_head="Future Enhancements",
        right_items=[
            "Variable panel count (3, 4, 5, 6)",
            "Local Stable Diffusion via diffusers",
            "Panel-level regeneration",
            "Art style presets (Manga, Noir, Retro)",
            "Speech bubble overlay on images",
            "Background task queue (async generation)",
            "Session history and comic gallery",
            "Social sharing via unique URL",
            "Grid and booklet PDF layouts",
        ]
    )

    # ── Slide 20: Conclusion ─────────────────────────────────────────────────
    _content_slide(prs, 20, "Conclusion", [
        "ComicCraft demonstrates a complete, production-oriented Generative AI pipeline",
        "",
        "Key contributions:",
        "  Google Gemini structured JSON output + Pydantic validation",
        "    → Reliable, type-safe AI responses without text parsing",
        "  Hugging Face hosted inference + multi-tier fallback",
        "    → Pipeline always completes regardless of API availability",
        "  FastAPI + auto-generated Swagger UI",
        "    → Documented API with minimal boilerplate",
        "  FPDF2 + Pillow server-side media generation",
        "    → No external services required for PDF or image fallback",
        "",
        "Principles demonstrated:",
        "  Structured AI output  ·  Graceful degradation",
        "  Pipeline validation   ·  Security-first file handling",
        "",
        "These principles apply directly to production Generative AI system design",
    ])

    prs.save(output_path)
    print(f"Presentation saved: {output_path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "ComicCraft_Presentation.pptx"
    build_presentation(out)
