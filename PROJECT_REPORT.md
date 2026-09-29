# PROJECT REPORT

## ComicCraft — AI Comic Story Creator

---

| Field | Detail |
|---|---|
| **Project Title** | ComicCraft: AI Comic Story Creator |
| **Technology Domain** | Generative AI / Web Application |
| **Technologies** | Python, FastAPI, Google Gemini, Hugging Face, FPDF2 |
| **Project Type** | Application Development |

---

## 1. Abstract

ComicCraft is a web-based Generative AI application that transforms a user's plain text story idea into a complete five-panel illustrated comic book. The system uses Google Gemini to generate a structured five-panel story outline and then expands it into a full comic script containing captions, narration, and character dialogue for each panel. Hugging Face hosted text-to-image inference is used to generate one illustrated panel image per story panel. The illustrated panels and narrative text are assembled into an HTML preview page and exported as a downloadable A4 PDF comic book using FPDF2.

The application is built on FastAPI with Jinja2 server-side rendering, Pydantic data validation, and a multi-tier fallback system that ensures the pipeline always completes — even when external AI APIs are temporarily unavailable. All input validation, image path security, and PDF download protection are implemented server-side.

---

## 2. Introduction

Comic storytelling is a popular and expressive medium used across entertainment, education, and communication. However, creating a comic from scratch requires a combination of narrative writing skill, illustration ability, and layout knowledge — skills that most people do not possess simultaneously.

Advances in large language models (LLMs) and text-to-image diffusion models now make it possible to automate both the narrative and visual components of comic creation. Google Gemini can generate structured, coherent multi-panel stories given a brief prompt. Hugging Face's hosted inference API provides access to state-of-the-art image generation models without requiring local GPU hardware.

ComicCraft integrates these two AI capabilities into a single, user-friendly web application. A user provides a story idea, a character name, a setting, a tone, and an art style. The system handles the rest — generating the story, creating the illustrations, laying out the comic, and producing a downloadable PDF — in a fully automated pipeline.

---

## 3. Problem Statement

Creating a comic story currently requires:

- **Strong narrative writing skills** to produce a multi-panel story with consistent characters, logical progression, and appropriate pacing
- **Illustration or digital art expertise** to produce panel images that visually match the story
- **Layout and publishing knowledge** to arrange panels, captions, and dialogue into a presentable format
- **Access to professional software** (Adobe Illustrator, Photoshop, InDesign) to combine the above elements

These requirements create a high barrier to entry. Hobbyists, students, educators, and casual users who have a story idea but lack artistic or writing skills have no accessible tool that bridges the complete gap from idea to finished, shareable comic.

Existing tools address only parts of this problem:
- General-purpose chatbots (ChatGPT) can write stories but produce no images or PDF output
- AI image tools (DALL·E, Midjourney) generate images but provide no structured narrative or export
- Comic builder tools (Canva, Pixton) offer clip-art panels but no original story or image AI
- Script-writing tools format dialogue but do not generate visuals or exports

No existing tool provides an end-to-end pipeline from a text prompt to a complete, illustrated, exportable comic book.

---

## 4. Existing System

### Current Approaches and Their Limitations

| Tool / Approach | What It Provides | What Is Missing |
|---|---|---|
| ChatGPT / LLM prompting | Story text | No images, no layout, no PDF export |
| DALL·E / Midjourney | Individual images | No narrative structure, no multi-panel layout, no story |
| Canva Comics | Pre-made clip-art layout | No AI story generation, no original images |
| Pixton | Character-based comic builder | Fixed clip-art characters, no AI text or image generation |
| Adobe Express | Graphic design templates | No AI story or image generation |
| Stable Diffusion (local) | High-quality AI images | No story pipeline, requires GPU hardware, no PDF output |

**Core gap:** None of these tools provide a complete pipeline that takes a plain text idea and automatically produces a structured multi-panel story, a matching set of AI-generated illustrations, and a formatted exportable PDF — without requiring artistic skill, specialized software, or hardware from the user.

---

## 5. Proposed System

ComicCraft proposes and implements a complete end-to-end Generative AI comic creation pipeline:

```
User text prompt
    → Google Gemini (outline generation)
    → Google Gemini (story script expansion)
    → Hugging Face (panel image generation × 5)
    → Layout builder (assembly and validation)
    → HTML comic preview (browser)
    → FPDF2 PDF export (downloadable)
```

**Key design principles:**

1. **Structured AI output:** Gemini is prompted to return strictly typed JSON matching Pydantic schemas — no text parsing or regex required
2. **Multi-tier fallback:** Both Gemini and Hugging Face include automatic model fallback chains; if all image generation fails, a styled local placeholder is generated so the pipeline always completes
3. **Strict validation:** Exactly 5 panels and 5 images are enforced at every stage — outline, story, layout builder, and PDF
4. **Security:** PDF download endpoint validates filenames against the exports directory to prevent path traversal; all inputs are Pydantic-validated before any API call
5. **Accessibility:** No user artistic or writing skill is required — only a plain text story idea

---

## 6. Objectives

1. **Story Generation:** Use Google Gemini to produce a coherent five-panel comic outline (title, scene description, image prompt per panel) and expand it into a full script (caption, narration, dialogue per panel)
2. **Image Generation:** Use Hugging Face hosted text-to-image inference to generate one AI illustration per panel at 768×1024 resolution
3. **5-Panel Validation:** Enforce that exactly 5 panels and 5 images are produced and matched at every stage of the pipeline
4. **Comic Preview:** Render a complete HTML comic preview immediately after generation, showing all 5 panels with their images and text
5. **PDF Export:** Generate and serve a professionally formatted, downloadable A4 PDF comic book using FPDF2
6. **Resilience:** Ensure the pipeline never crashes due to external API failures — implement graceful fallback at every layer
7. **API Documentation:** Provide auto-generated interactive API documentation (Swagger UI) through FastAPI
8. **Security:** Validate all user inputs, enforce filename security on downloads, and never expose API keys in responses

---

## 7. System Architecture

### Overview

The application follows a linear pipeline architecture with validation checkpoints at each stage. All processing is server-side. The browser communicates via HTML form POST or JSON REST API.

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                             │
│  GET /          →  index.html (story input form)               │
│  POST /generate →  HTML form submission                        │
│  POST /generate-comic/json  →  REST API                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Application Layer                       │
│                       (routes.py)                               │
│                                                                 │
│  Step 1: Input validation (Pydantic PromptRequest)             │
│                                                                 │
│  Step 2: gemini_flash.py → generate_outline()                  │
│          └── gemini_client.py → Google Gemini API              │
│               Returns: ComicOutline (5 × PanelOutline)         │
│                                                                 │
│  Step 3: gemini_pro.py → generate_story()                      │
│          └── gemini_client.py → Google Gemini API              │
│               Returns: ComicStory (5 × PanelStory)             │
│                                                                 │
│  Step 4: image_generator.py → generate_image() × 5            │
│          └── HuggingFace InferenceClient                       │
│               Fallback: Pillow placeholder image               │
│               Returns: 5 PNG paths in static/panels/           │
│                                                                 │
│  Step 5: layout_builder.py → build_comic_layout()              │
│          Validates: exactly 5 panels + 5 images                │
│          Returns: List[ComicPanel]                             │
│                                                                 │
│  Step 6: exporters.py → save_pdf()                             │
│          FPDF2 → A4 PDF → static/exports/                      │
│                                                                 │
│  Step 7: Jinja2 → comic_preview.html rendered                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
              GET /download/{filename}
              FileResponse → PDF streamed to browser
```

### Component Relationships

```
config.py           ← loaded by all modules (Settings, paths)
models.py           ← Pydantic schemas used across all modules
gemini_client.py    ← used by gemini_flash.py and gemini_pro.py
gemini_flash.py  ┐
gemini_pro.py    ├─ called by routes.py
image_generator.py│
layout_builder.py│
exporters.py     ┘
routes.py           ← FastAPI router registered in main.py
main.py             ← app factory, mounts static files
```

---

## 8. Technologies Used

| Technology | Version Constraint | Role |
|---|---|---|
| Python | 3.10+ | Core application language |
| FastAPI | ≥0.115 | Web framework: routing, validation, auto-docs |
| Uvicorn | ≥0.30 | ASGI server |
| Jinja2 | ≥3.1 | Server-side HTML template rendering |
| google-genai | ≥1.30 | Google Gemini API client |
| huggingface-hub | ≥0.34 | Hugging Face InferenceClient |
| Pydantic | ≥2.8 | Data models, request validation, structured parsing |
| pydantic-settings | ≥2.5 | Environment-based configuration management |
| FPDF2 | ≥2.8 | PDF generation and export |
| Pillow | ≥10 | Fallback placeholder image creation |
| python-dotenv | ≥1.0 | `.env` file loading |
| python-multipart | ≥0.0.9 | HTML form data parsing |
| pytest | ≥8 | Test framework |
| httpx | ≥0.27 | HTTP client (available for testing) |
| HTML/CSS/JS | — | Frontend: form, loading state, comic preview layout |

---

## 9. System Modules

### 9.1 Configuration Module (`app/config.py`)

Manages all application settings using `pydantic-settings`. Settings are loaded from the `.env` file using `SettingsConfigDict`. The `get_settings()` function is decorated with `@lru_cache` so the settings object is created once and reused. On first call, it also creates the `static/panels/` and `static/exports/` output directories.

**Key settings:** `GEMINI_API_KEY`, `HF_TOKEN`, `GEMINI_OUTLINE_MODEL`, `GEMINI_STORY_MODEL`, `HF_IMAGE_MODEL`, `HF_PROVIDER`, `IMAGE_WIDTH`, `IMAGE_HEIGHT`, `IMAGE_STEPS`

### 9.2 Data Models (`app/models.py`)

Defines all Pydantic data structures used throughout the pipeline:

| Model | Purpose |
|---|---|
| `PromptRequest` | Validates the five user input fields (with character and length constraints) |
| `PanelOutline` | One panel in the Gemini outline: number, title, scene description, image prompt |
| `ComicOutline` | Container for `List[PanelOutline]` — the structured Gemini outline response |
| `PanelStory` | Expanded panel: adds caption, narration, dialogue to `PanelOutline` fields |
| `ComicStory` | Container for `List[PanelStory]` — the structured Gemini story response |
| `ComicPanel` | Assembled panel with all story fields plus resolved image path |
| `GenerateResponse` | JSON API response: `success`, `panels`, `pdf_url`, `pdf_filename` |

### 9.3 Gemini Client (`app/gemini_client.py`)

Low-level Gemini API interface. `generate_structured(model, prompt, schema)` sends a prompt to Gemini requesting `application/json` output matching a given Pydantic schema. The response is returned as a fully parsed Pydantic object via `response.parsed` or `schema.model_validate_json(text)`. Implements a fallback chain across configured Gemini models with specific error classification for 404, 429, 500/503, and 401/403 responses.

### 9.4 Outline Generator (`app/gemini_flash.py`)

Calls `generate_structured` with the `ComicOutline` schema and a prompt that instructs Gemini to produce exactly 5 panels. Validates the returned panel count and raises `RuntimeError` if it is not 5.

### 9.5 Story Generator (`app/gemini_pro.py`)

Calls `generate_structured` with the `ComicStory` schema and a prompt that expands the outline JSON into a full comic script. Preserves panel numbers, titles, scene descriptions, and image prompts from the outline while adding caption, narration, and dialogue. Validates the returned panel count.

### 9.6 Image Generator (`app/image_generator.py`)

Calls `InferenceClient.text_to_image()` for each panel's `image_prompt`. Saves the resulting PIL Image as a PNG to `static/panels/`. If `HF_TOKEN` is absent or all HF model attempts fail, calls `_create_placeholder_image()` to generate a styled comic panel illustration using Pillow drawing primitives. Returns the web-relative image path (`/static/panels/<filename>`).

### 9.7 Layout Builder (`app/layout_builder.py`)

Receives a `ComicStory` and a list of 5 image paths. Validates that both contain exactly 5 items and that the counts match. Assembles and returns `List[ComicPanel]` by zipping story panels with image paths.

### 9.8 Exporters (`app/exporters.py`)

`save_pdf(layout, title)` iterates over the 5 `ComicPanel` objects and creates a multi-page A4 PDF using FPDF2. Each page contains: panel title heading, centered panel image, scene description, caption, narration, and (if present) dialogue. `_resolve_image_path()` handles Windows and Unix path normalization for FPDF2 image loading.

### 9.9 Routes (`app/routes.py`)

Registers all HTTP endpoints with FastAPI. The core function `_generate_comic(data)` orchestrates the five-step pipeline: outline → story → images → layout → PDF. Error handling catches all exceptions and returns a user-friendly error page rather than a stack trace.

### 9.10 Application Entry Point (`app/main.py`)

Creates the `FastAPI` app instance, mounts `static/` as a static file directory, registers the router, and exposes the `/health` endpoint.

---

## 10. AI Workflow

### Stage 1 — Five-Panel Story Outline

**Module:** `gemini_flash.py` → `gemini_client.generate_structured()`

**Input to Gemini:**
```
Create a coherent five-panel comic outline.
User story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Requirements:
- Return exactly 5 panels.
- Give each panel a concise title.
- scene_description explains what happens visually.
- image_prompt is a detailed text-to-image prompt.
- Maintain character consistency and the requested art style.
- Family-friendly, no copyrighted characters.
```

**Gemini output mode:** `response_mime_type="application/json"` with `response_schema=ComicOutline`

**Output:** `ComicOutline` — a list of 5 `PanelOutline` objects, each containing `panel_number`, `title`, `scene_description`, `image_prompt`

---

### Stage 2 — Comic Script Expansion

**Module:** `gemini_pro.py` → `gemini_client.generate_structured()`

**Input to Gemini:** The serialized `ComicOutline` JSON plus a prompt requesting expansion into a full comic script.

**Gemini output mode:** `response_mime_type="application/json"` with `response_schema=ComicStory`

**Output:** `ComicStory` — a list of 5 `PanelStory` objects, adding `caption`, `narration`, and `dialogue` to each panel

---

### Stage 3 — Panel Image Generation

**Module:** `image_generator.generate_image()`

For each of the 5 panels, the `image_prompt` is augmented with style consistency instructions and sent to `InferenceClient.text_to_image()`. The returned PIL Image is saved as a PNG. If generation fails, the Pillow-based placeholder is used.

---

## 11. Backend Implementation

### FastAPI Application

The application is created in `main.py` using `FastAPI(title=..., description=..., version="1.0.0")`. Static files are served from `static/` at the `/static` URL prefix using `StaticFiles`. The main router is registered via `app.include_router(router)`.

### HTTP Endpoints

| Endpoint | Method | Response Type | Purpose |
|---|---|---|---|
| `/` | GET | HTML | Home page — story form |
| `/generate` | POST | HTML | Form-based comic generation |
| `/generate-comic/json` | POST | JSON | API-based comic generation |
| `/download/{filename}` | GET | File | PDF download |
| `/test-image` | GET | JSON | Image generation test |
| `/health` | GET | JSON | Liveness check |
| `/export-success` | GET | HTML | Export confirmation |

### Input Validation

All user inputs are validated by Pydantic's `PromptRequest` model before any API call is made. Field constraints:
- `story_prompt`: 3–2000 characters
- `character_name`: 1–80 characters
- `setting`: 1–120 characters
- `tone`: 1–60 characters
- `art_style`: 1–80 characters

### Error Handling

The `/generate` endpoint wraps the entire pipeline in a `try/except`. On any exception, the error message is rendered in `index.html` with HTTP 500, rather than returning a raw stack trace. The `/generate-comic/json` endpoint raises `HTTPException(500)` with the error detail.

---

## 12. Frontend Implementation

### Templates

Three Jinja2 HTML templates are used:

- **`index.html`** — Main story input form with five fields, client-side validation, loading spinner on submit, and inline error display
- **`comic_preview.html`** — Comic display page iterating over `layout` (the `List[ComicPanel]`), rendering each panel's title, image, caption, narration, and dialogue in a styled card layout, with a "Download PDF" button
- **`export_success.html`** — Simple confirmation page shown after export

### Styling

`static/css/style.css` provides:
- Dark-themed comic aesthetic
- Animated loading spinner displayed during generation
- Responsive panel card layout
- Hover effects on interactive elements

### JavaScript

Minimal vanilla JavaScript handles:
- Form submission loading state (showing the spinner and disabling the submit button)
- Basic form validation feedback

No JavaScript framework is used. All content rendering is server-side.

---

## 13. Gemini Integration

### Client Initialization (`gemini_client.get_client()`)

Creates a `genai.Client` using the `GEMINI_API_KEY` from settings. Raises `RuntimeError` immediately if the key is absent or is the placeholder value `"your_gemini_api_key_here"`.

### Structured Output (`gemini_client.generate_structured()`)

Calls `client.models.generate_content()` with:
- `response_mime_type="application/json"` — instructs Gemini to return valid JSON
- `response_schema=<PydanticModel>` — constrains the JSON structure to the exact schema

The response is parsed via `response.parsed` (if available) or `schema.model_validate_json(response.text)`.

### Fallback Chain

If the primary model fails, the function iterates through `gemini_fallback_models`:
```
gemini-flash-lite-latest → gemini-3.8-flash → gemini-3.5-flash →
gemini-3.1-flash-lite → gemini-flash-latest
```

Error classification:
- **404 / NOT_FOUND** → try next model (model deprecated or unavailable)
- **429 / RESOURCE_EXHAUSTED** → try next model (quota exceeded)
- **500 / 503 / UNAVAILABLE** → try next model (service overloaded)
- **401 / 403 / API_KEY_INVALID** → raise immediately (key issue, fallback won't help)

---

## 14. Hugging Face Image Generation

### Inference Client

`image_generator.generate_image()` uses `huggingface_hub.InferenceClient` with `provider=settings.hf_provider` and `api_key=settings.hf_token`. The `text_to_image()` method is called with:
- `prompt`: the panel's `image_prompt` augmented with style consistency instructions
- `model`: the configured HF model name
- `width`: 768, `height`: 1024, `num_inference_steps`: 28

### Default and Fallback Models

```
Primary: stabilityai/stable-diffusion-3-medium-diffusers
Fallbacks: black-forest-labs/FLUX.1-schnell → ByteDance/SDXL-Lightning
```

### Two-Tier Fallback

**Tier 1:** If `HF_TOKEN` is absent or is the placeholder string `"your_huggingface_token_here"`, the function skips HF entirely and calls `_create_placeholder_image()` immediately.

**Tier 2:** If a model call raises any exception, the next model in the list is tried. If all HF models fail, `_create_placeholder_image()` is called.

### Placeholder Image

`_create_placeholder_image()` uses Pillow drawing primitives to produce a 768×1024 PNG with:
- Dark background (`#2b2d42`)
- Double comic frame border
- Red "PANEL N" badge
- Center illustration box with a comic icon
- Wrapped prompt text summary
- A note explaining why the placeholder was used

---

## 15. Five-Panel Comic Layout

### Validation (`layout_builder.build_comic_layout()`)

Before assembling the layout, three validations are performed:

```python
if len(story.panels) != 5:
    raise ValueError(f"Comic must contain exactly 5 panels; received {len(story.panels)}.")

if len(image_paths) != 5:
    raise ValueError(f"Comic requires exactly 5 images; received {len(image_paths)}.")

if len(story.panels) != len(image_paths):
    raise ValueError("Every story panel must have exactly one corresponding generated image.")
```

### Assembly

Each `PanelStory` is combined with its corresponding image path to produce a `ComicPanel`. The `List[ComicPanel]` is the unified data structure passed to both the Jinja2 template and the PDF exporter.

---

## 16. PDF Generation

### Structure

`exporters.save_pdf()` creates an A4 portrait PDF using FPDF2. One page is generated per panel:

```
Page layout (A4, 210mm × 297mm, margins 15mm):
├── Panel title          Helvetica Bold 18pt
├── Panel image          160mm wide, centered, y=30mm
├── Scene description    Helvetica Italic 10pt
├── Caption              Helvetica Bold 11pt (label) + Regular 10pt (text)
├── Narration            Helvetica Bold 11pt (label) + Regular 10pt (text)
└── Dialogue             Helvetica Bold 11pt (label) + Regular 10pt (text)
                         [only included if dialogue is non-empty]
```

### Image Path Resolution

`_resolve_image_path()` implements a multi-strategy resolver to handle Windows and Unix path differences for FPDF2:

1. If path starts with `/static/` or `static/`, resolve relative to `settings.output_dir`
2. Try the filename directly in `settings.panels_dir`
3. Try as a direct filesystem path
4. Try relative to `settings.output_dir.parent`

If the resolved file still does not exist, an emergency grey placeholder image is created using Pillow before the PDF renders.

### Security

The `/download/{filename}` endpoint resolves the full path and checks:
```python
if requested.parent != settings.exports_dir.resolve():
    raise HTTPException(status_code=400, detail="Invalid filename.")
```
This prevents any path traversal attempt (e.g. `../../.env`) from reaching the filesystem.

---

## 17. Error Handling and Fallbacks

### Gemini Error Table

| HTTP Code | Condition | Action |
|---|---|---|
| 404 / NOT_FOUND | Model deprecated or unavailable | Try next fallback model |
| 429 / RESOURCE_EXHAUSTED | API quota exceeded | Try next fallback model |
| 500 / 502 / 503 / 504 | Service overloaded / unavailable | Try next fallback model |
| 401 / 403 | Invalid or unauthorised API key | Raise `RuntimeError` immediately |
| All models fail | Exhausted fallback chain | Raise `RuntimeError` with last message |

### Image Generation Error Table

| Condition | Action |
|---|---|
| `HF_TOKEN` not set or is placeholder | Skip HF; create Pillow placeholder |
| HF model call fails | Try next model in `hf_fallback_models` |
| All HF models fail | Create Pillow placeholder |
| Image file missing at PDF time | Create emergency grey image via Pillow |

### Request Validation Errors

| Scenario | Action |
|---|---|
| Empty or too-short field | Pydantic `ValidationError` → `index.html` with error |
| Field exceeds max length | Pydantic `ValidationError` → `index.html` with error |
| Gemini / HF pipeline fails | Caught by `try/except` → `index.html` with error message |
| JSON API fails | `HTTPException(500)` with `detail` string |

---

## 18. Testing

### Test Suite (`tests/test_core.py`)

The project includes four automated tests using pytest:

**`test_layout_builder_validates_five_panels`**  
Creates a mock `ComicStory` with 5 panels and 5 image paths. Calls `build_comic_layout()` and asserts the result contains exactly 5 `ComicPanel` objects with correct `panel_number` and `image_path` values.

**`test_layout_builder_rejects_non_five_panels`**  
Creates a mock `ComicStory` with 4 panels and 4 image paths. Asserts that `build_comic_layout()` raises a `ValueError` matching `"Comic must contain exactly 5 panels"`.

**`test_layout_builder_rejects_mismatched_images`**  
Creates a mock `ComicStory` with 5 panels but only 4 image paths. Asserts that `build_comic_layout()` raises a `ValueError` matching `"Comic requires exactly 5 images"`.

**`test_pdf_export_and_path_resolution`**  
Calls `generate_image()` five times to produce 5 local placeholder images (no HF token required). Builds a layout with `build_comic_layout()`. Calls `save_pdf()` and asserts the resulting PDF file exists on disk and has a size greater than 1000 bytes.

### Running Tests

```bash
pytest -v
```

All 4 tests pass in approximately 0.6 seconds without requiring any API credentials.

### Test Coverage

| Component | Tested By |
|---|---|
| Layout builder — valid input | `test_layout_builder_validates_five_panels` |
| Layout builder — panel count validation | `test_layout_builder_rejects_non_five_panels` |
| Layout builder — image count validation | `test_layout_builder_rejects_mismatched_images` |
| Image generator — HF fallback | `test_pdf_export_and_path_resolution` |
| PDF exporter — file creation | `test_pdf_export_and_path_resolution` |
| Path resolver — image path handling | `test_pdf_export_and_path_resolution` |

---

## 19. Results

### Functional Outcomes

| Capability | Status |
|---|---|
| Google Gemini story outline generation | Implemented and working |
| Google Gemini script expansion with caption/narration/dialogue | Implemented and working |
| Hugging Face text-to-image generation | Implemented and working (requires HF_TOKEN) |
| Fallback placeholder image generation | Implemented and always available |
| Strict 5-panel + 5-image validation | Implemented at outline, story, layout, and PDF stages |
| HTML comic preview | Implemented and working |
| A4 PDF export with per-panel images and text | Implemented and working |
| Swagger UI auto-documentation | Available at `/docs` |
| JSON REST API endpoint | Implemented at `POST /generate-comic/json` |
| Path traversal protection on downloads | Implemented in `/download/{filename}` |
| Automated test suite | 4 tests — all passing |

### Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-8.4.2
collected 4 items

tests/test_core.py::test_layout_builder_validates_five_panels  PASSED
tests/test_core.py::test_layout_builder_rejects_non_five_panels PASSED
tests/test_core.py::test_layout_builder_rejects_mismatched_images PASSED
tests/test_core.py::test_pdf_export_and_path_resolution        PASSED

4 passed in 0.64s
==============================
```

---

## 20. Limitations

| Limitation | Description |
|---|---|
| **Fixed 5-panel output** | The pipeline is hardcoded for exactly 5 panels; variable counts are not supported |
| **Gemini structured output reliability** | Very rarely, Gemini may return malformed JSON, causing a generation error that requires retry |
| **HF inference latency** | Generating 5 images via hosted inference typically takes 30–90 seconds depending on model load |
| **HF free tier rate limits** | The free Hugging Face plan has strict request rate limits; frequent use triggers 429 errors and fallback to placeholders |
| **PDF font encoding** | FPDF2 built-in fonts (Helvetica) do not support the full Unicode range; non-latin-1 characters are replaced |
| **No session or user history** | Generated comics and PDFs are stored in `static/panels/` and `static/exports/` but are not associated with any session or user |
| **No content moderation layer** | User prompts are passed directly to Gemini; Gemini's own safety filters apply but no additional moderation is implemented |
| **Blocking HTTP requests** | Image generation runs synchronously within the HTTP request cycle; the browser blocks for the full generation duration |
| **Windows path specifics** | The image path resolver includes Windows-specific normalization; cross-platform compatibility is maintained through multi-strategy resolution |

---

## 21. Future Enhancements

| Enhancement | Description |
|---|---|
| **Variable panel count** | Allow the user to select 3, 4, 5, or 6 panels |
| **Local image generation** | Support offline Stable Diffusion via the `diffusers` library as an alternative to hosted HF inference |
| **Panel-level regeneration** | Regenerate a single panel without rerunning the entire pipeline |
| **Art style presets** | Pre-built prompting templates for Manga, Noir, Watercolor, Retro, Superhero styles |
| **Speech bubble overlay** | Render dialogue as actual speech bubbles overlaid on panel images using Pillow |
| **Background task queue** | Move image generation to an async task queue so the HTTP request returns immediately with a polling mechanism |
| **Session history and gallery** | Store generated comics per session and provide a browsable gallery |
| **Social sharing** | Generate unique public URLs for comic previews |
| **Alternative PDF layouts** | Grid layout (all panels on one page) and booklet format |
| **User accounts** | Authentication and personal comic library |

---

## 22. Conclusion

ComicCraft demonstrates a complete, production-oriented Generative AI pipeline assembled from modern Python components. The project shows how Google Gemini's structured JSON output mode can be combined with Pydantic's strict type validation to produce reliable, machine-readable AI responses — eliminating the fragility of text parsing. It shows how Hugging Face's hosted inference API can be integrated with a multi-tier fallback that guarantees pipeline completion regardless of external API availability.

The FastAPI framework provides a clean, auto-documented API surface with minimal boilerplate. Pydantic enforces data integrity at every boundary. FPDF2 and Pillow handle all media production server-side without external services. The result is an application that is both robust — never crashing due to AI API failures — and accessible — requiring only a text prompt from the user.

The principles demonstrated here — structured AI output, graceful degradation, pipeline validation, and security-first file handling — apply directly to the design of production Generative AI systems.

---

## 23. References

1. Google AI Studio — Gemini API Documentation  
   https://ai.google.dev/

2. Hugging Face — Inference API Documentation  
   https://huggingface.co/docs/api-inference/

3. FastAPI — Documentation  
   https://fastapi.tiangolo.com/

4. Pydantic v2 — Documentation  
   https://docs.pydantic.dev/latest/

5. pydantic-settings — Documentation  
   https://docs.pydantic.dev/latest/concepts/pydantic_settings/

6. FPDF2 — Python PDF Library Documentation  
   https://py-pydantic.github.io/fpdf2/

7. Pillow (PIL Fork) — Documentation  
   https://pillow.readthedocs.io/

8. huggingface-hub — Python Client Library  
   https://huggingface.co/docs/huggingface_hub/

9. Uvicorn — ASGI Server Documentation  
   https://www.uvicorn.org/

10. Jinja2 — Template Engine Documentation  
    https://jinja.palletsprojects.com/

11. Stability AI — Stable Diffusion 3 Model Card  
    https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers

12. Black Forest Labs — FLUX.1-schnell Model  
    https://huggingface.co/black-forest-labs/FLUX.1-schnell

13. pytest — Testing Framework  
    https://docs.pytest.org/

---

*ComicCraft: AI Comic Story Creator — Project Report*
