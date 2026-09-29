# 🎨 ComicCraft — AI Comic Story Creator

> Transform any story idea into a five-panel comic book with AI-generated narrative and illustrated panels — powered by Google Gemini and Hugging Face.

---

## 📌 Problem Statement

Creating a comic story from scratch requires both strong narrative writing and visual illustration skills — a combination that is time-consuming and inaccessible to most people. There is no simple tool that lets anyone, regardless of artistic ability, turn a plain text idea into a complete, visually illustrated comic story that can be exported and shared.

---

## 🎯 Project Objectives

- Allow any user to generate a five-panel AI comic story from a single text prompt
- Use Google Gemini to produce a coherent, structured narrative with a consistent character and setting
- Use Hugging Face hosted text-to-image inference to generate actual illustrated panels
- Provide graceful fallback when image generation is unavailable, so the full workflow always completes
- Export the finished comic as a downloadable PDF document

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Structured Story Generation** | Gemini generates a coherent five-panel outline and then expands each panel into a full script with caption, narration, and optional dialogue |
| **AI Image Generation** | Hugging Face hosted inference generates one illustrated panel image per story panel |
| **Automatic Fallback** | If HF token is missing or all HF models fail, a clean comic-styled placeholder image is generated locally so the workflow never breaks |
| **5-Panel Validation** | The app strictly validates that exactly 5 panels and 5 images are produced at every stage |
| **Comic Preview** | After generation, a full HTML comic preview page is rendered in the browser |
| **PDF Export** | A professionally formatted A4 PDF is generated with images, captions, narration, and dialogue for every panel |
| **Model Fallback Chain** | Both Gemini and Hugging Face include automatic fallback across a configurable list of models |
| **Secure Downloads** | The PDF download endpoint validates filenames and prevents path traversal attacks |
| **JSON API** | A JSON endpoint is available for programmatic / API-first access |
| **Interactive UI** | A web form lets users enter prompt, character, setting, tone, and art style with real-time loading feedback |

---

## 🏗 System Architecture

```
User Browser
    │
    │  POST /generate (HTML form)
    │  POST /generate-comic/json (REST API)
    ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                       │
│                                                             │
│  routes.py  →  _generate_comic()                           │
│      │                                                      │
│      ├─ 1. gemini_flash.py  →  generate_outline()          │
│      │       └─ gemini_client.py → Google Gemini API       │
│      │              Returns: ComicOutline (5 PanelOutlines) │
│      │                                                      │
│      ├─ 2. gemini_pro.py  →  generate_story()              │
│      │       └─ gemini_client.py → Google Gemini API       │
│      │              Returns: ComicStory (5 PanelStory)     │
│      │                                                      │
│      ├─ 3. image_generator.py  →  generate_image() × 5    │
│      │       └─ Hugging Face InferenceClient               │
│      │              ↳ Fallback: PIL placeholder image      │
│      │              Returns: 5 image paths                 │
│      │                                                      │
│      ├─ 4. layout_builder.py  →  build_comic_layout()      │
│      │              Validates 5 panels + 5 images          │
│      │              Returns: List[ComicPanel]              │
│      │                                                      │
│      └─ 5. exporters.py  →  save_pdf()                     │
│                 FPDF2 → A4 PDF saved to static/exports/    │
│                                                             │
│  Jinja2 renders comic_preview.html                         │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
GET /download/{filename}  →  FileResponse (PDF)
```

---

## 🔄 Complete Workflow

```
1. User submits form
   story_prompt, character_name, setting, tone, art_style
         │
         ▼
2. Gemini Flash (gemini_flash.py)
   Generates structured ComicOutline
   → 5 PanelOutline objects (title, scene_description, image_prompt)
         │
         ▼
3. Gemini (gemini_pro.py)
   Expands outline into full ComicStory
   → 5 PanelStory objects (adds caption, narration, dialogue)
         │
         ▼
4. Hugging Face text-to-image (image_generator.py)
   One generate_image() call per panel (5 calls total)
   → 5 PNG files saved to static/panels/
   → Falls back to styled placeholder if HF is unavailable
         │
         ▼
5. Layout Builder (layout_builder.py)
   Validates exactly 5 panels and 5 image paths
   → List[ComicPanel] assembled
         │
         ▼
6. PDF Export (exporters.py)
   FPDF2 creates multi-page A4 PDF
   → Saved to static/exports/comiccraft_<timestamp>.pdf
         │
         ▼
7. Comic Preview
   Jinja2 renders comic_preview.html
   → Browser displays all 5 panels with images, captions, narration
         │
         ▼
8. PDF Download
   GET /download/<filename>
   → FileResponse streams the PDF to the browser
```

---

## 🛠 Technologies

| Technology | Role |
|---|---|
| **Python 3.10+** | Core application language |
| **FastAPI** | Web framework, HTTP routing, form handling, JSON API |
| **Uvicorn** | ASGI server |
| **Jinja2** | Server-side HTML template rendering |
| **Google Gemini** (`google-genai`) | AI narrative generation — outline and story script |
| **Hugging Face Inference** (`huggingface-hub`) | Text-to-image generation for panel illustrations |
| **Pydantic / pydantic-settings** | Request validation, structured response parsing, settings management |
| **FPDF2** | PDF generation and export |
| **Pillow (PIL)** | Fallback placeholder image creation; image path validation |
| **python-dotenv** | `.env` file loading |
| **HTML / CSS / JavaScript** | Frontend form, loading state, comic preview layout |
| **pytest + httpx** | Test suite |

---

## 📁 Project Structure

```
ComicCraft/
├── app/                        # Application package
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory, static file mount
│   ├── config.py               # Settings (pydantic-settings, .env loading)
│   ├── models.py               # Pydantic models (PromptRequest, ComicPanel, etc.)
│   ├── routes.py               # All HTTP endpoints
│   ├── gemini_client.py        # Gemini client, fallback chain, error formatting
│   ├── gemini_flash.py         # Outline generation (5-panel ComicOutline)
│   ├── gemini_pro.py           # Story/script expansion (ComicStory)
│   ├── image_generator.py      # HF image generation + fallback placeholder
│   ├── layout_builder.py       # 5-panel validation and layout assembly
│   └── exporters.py            # PDF generation with FPDF2
│
├── templates/                  # Jinja2 HTML templates
│   ├── index.html              # Home page — story prompt form
│   ├── comic_preview.html      # Comic preview with all 5 panels
│   └── export_success.html     # Export confirmation page
│
├── static/                     # Static file root (served at /static)
│   ├── css/
│   │   └── style.css           # Application stylesheet
│   ├── panels/                 # Generated panel images (PNG)
│   │   └── .gitkeep
│   └── exports/                # Generated PDFs
│       └── .gitkeep
│
├── tests/
│   └── test_core.py            # pytest test suite
│
├── .env                        # Local secrets (NOT committed to git)
├── .env.example                # Template for .env — copy and fill in credentials
├── .gitignore                  # Excludes .env, venvs, generated media, PDFs
├── requirements.txt            # Python dependencies with version constraints
└── README.md                   # This file
```

---

## ⚙️ Requirements

- Python **3.10** or later
- A **Google Gemini API key** — [Get one at Google AI Studio](https://aistudio.google.com/)
- A **Hugging Face token** (optional, but required for real image generation) — [Create one here](https://huggingface.co/settings/tokens)

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd ComicCraft
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy the example file
cp .env.example .env    # Linux / macOS
copy .env.example .env  # Windows
```

Then open `.env` and fill in your real credentials (see [Environment Variables](#-environment-variables) below).

---

## 🔐 Environment Variables

Copy `.env.example` to `.env` and set the following values:

```env
# Required — Google Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here

# Required for real image generation — Hugging Face token
# If omitted, the app uses styled placeholder images automatically.
HF_TOKEN=your_huggingface_token_here

# Gemini model selection (these defaults are recommended)
GEMINI_OUTLINE_MODEL=gemini-flash-lite-latest
GEMINI_STORY_MODEL=gemini-flash-lite-latest

# Hugging Face text-to-image model and provider
HF_IMAGE_MODEL=stabilityai/stable-diffusion-3-medium-diffusers
HF_PROVIDER=hf-inference

# Image generation dimensions and quality
IMAGE_WIDTH=768
IMAGE_HEIGHT=1024
IMAGE_STEPS=28
```

> **Important:** Never commit `.env` to version control. It is listed in `.gitignore`.

---

## ▶️ Running the Application

```bash
# Make sure your virtual environment is active
uvicorn app.main:app --reload
```

The application starts at **http://127.0.0.1:8000**.

| URL | Description |
|---|---|
| `http://127.0.0.1:8000` | Home page — story form |
| `http://127.0.0.1:8000/health` | Health check |
| `http://127.0.0.1:8000/docs` | Interactive Swagger API docs |
| `http://127.0.0.1:8000/redoc` | ReDoc API documentation |

---

## 📡 API Endpoints

### `GET /`
Renders the home page with the comic story input form.

---

### `POST /generate`
**Form submission** — generates a full comic and returns the `comic_preview.html` page.

**Form fields:**

| Field | Type | Constraints | Description |
|---|---|---|---|
| `story_prompt` | `string` | 3–2000 chars | The main story idea |
| `character_name` | `string` | 1–80 chars | The main character's name |
| `setting` | `string` | 1–120 chars | Where the story takes place |
| `tone` | `string` | 1–60 chars | Emotional tone (e.g. Adventurous, Funny) |
| `art_style` | `string` | 1–80 chars | Visual style (e.g. Comic Book, Watercolor) |

**Success:** Returns `comic_preview.html` with all 5 panels.  
**Error:** Returns `index.html` with an error message and HTTP 500.

---

### `POST /generate-comic/json`
**JSON API** — same generation pipeline, returns structured JSON response.

**Request body (`application/json`):**
```json
{
  "story_prompt": "A brave fox discovers a magical forest",
  "character_name": "Luna",
  "setting": "Enchanted Forest",
  "tone": "Adventurous",
  "art_style": "Comic Book"
}
```

**Response (`GenerateResponse`):**
```json
{
  "success": true,
  "panels": [
    {
      "panel_number": 1,
      "title": "The Discovery",
      "image_path": "/static/panels/panel_1_....png",
      "scene_description": "...",
      "caption": "...",
      "narration": "...",
      "dialogue": "...",
      "image_prompt": "..."
    }
  ],
  "pdf_url": "/download/comiccraft_20260929_131900.pdf",
  "pdf_filename": "comiccraft_20260929_131900.pdf"
}
```

---

### `GET /download/{filename}`
Streams a generated PDF file from `static/exports/`.

- Validates that the filename stays within `static/exports/` (prevents path traversal)
- Returns HTTP 404 if the file does not exist
- Returns HTTP 400 for invalid filenames

---

### `GET /test-image`
Test endpoint to verify Hugging Face image generation is working.

**Query parameter:** `prompt` (optional, has default value)

**Response:**
```json
{ "success": true, "image_url": "/static/panels/panel_0_....png" }
```

---

### `GET /health`
Service health check.

**Response:** `{ "status": "ok", "service": "ComicCraft" }`

---

### `GET /export-success`
Renders the export confirmation page.

---

## 🧪 Testing

The test suite uses **pytest** and covers the core pipeline without making real API calls.

```bash
# From the ComicCraft directory with your virtual environment active
pytest -v
```

### What is tested

| Test | Description |
|---|---|
| `test_layout_builder_validates_five_panels` | Verifies that a valid 5-panel story with 5 image paths produces a correct layout |
| `test_layout_builder_rejects_non_five_panels` | Confirms `ValueError` is raised when fewer than 5 panels are provided |
| `test_layout_builder_rejects_mismatched_images` | Confirms `ValueError` is raised when image count does not match panel count |
| `test_pdf_export_and_path_resolution` | Generates placeholder panel images using `generate_image()`, builds a layout, runs `save_pdf()`, and asserts a valid non-empty PDF file is created on disk |

> All tests run offline without requiring Gemini or Hugging Face credentials, because `generate_image()` automatically falls back to local placeholder images when `HF_TOKEN` is not configured.

---

## ⚠️ Error Handling and Fallback Behavior

### Gemini API errors

The `gemini_client.generate_structured()` function handles all Gemini errors with a configurable fallback chain:

| Condition | Behavior |
|---|---|
| **404 / Model not found** | Logs a warning and tries the next model in `GEMINI_FALLBACK_MODELS` |
| **429 / Quota exceeded** | Logs a warning and tries the next fallback model |
| **503 / Service overloaded** | Logs a warning and tries the next fallback model |
| **401 / 403 / Invalid key** | Raises `RuntimeError` immediately — no fallback attempted (the key is the issue) |
| **All models exhausted** | Raises `RuntimeError` with the last friendly error message |

Fallback model order (configurable in `.env`):
```
gemini-flash-lite-latest → gemini-3.8-flash → gemini-3.5-flash → gemini-3.1-flash-lite → gemini-flash-latest
```

### Hugging Face image generation errors

The `image_generator.generate_image()` function handles all HF errors with a two-tier fallback:

| Condition | Behavior |
|---|---|
| **HF_TOKEN missing / placeholder** | Immediately creates a styled local placeholder image; logs a warning |
| **HF model fails (any error)** | Tries the next model in `HF_FALLBACK_MODELS` |
| **All HF models fail** | Creates a styled local placeholder image; logs a warning |

The fallback placeholder image is a branded comic-styled illustration that preserves the complete workflow: the preview page and PDF export **always succeed** regardless of HF availability.

### Request validation

- All form fields are validated by Pydantic before processing begins
- Invalid inputs return `index.html` with a clear error message
- The layout builder enforces exactly 5 panels and 5 images at assembly time
- Both Gemini outline and story generation validate the returned panel count

### PDF download security

- The `/download/{filename}` endpoint resolves the requested path and verifies it lies within `static/exports/`
- Any path traversal attempt (e.g. `../../.env`) returns HTTP 400
- Non-existent files or non-PDF extensions return HTTP 404

---

## ⚡ Limitations

- **Exactly 5 panels only** — the generation pipeline is hardcoded for a 5-panel comic. Variable panel counts are not supported.
- **Gemini structured output** — relies on Gemini's JSON mode. Very rarely, the model may return a malformed structure that causes a generation error.
- **Hugging Face inference latency** — generating 5 images via the hosted inference API can take 30–120 seconds depending on model load and plan tier.
- **HF free tier rate limits** — the free Hugging Face plan has strict rate limits; frequent generation will trigger 429 errors, causing the fallback placeholder to be used.
- **PDF font encoding** — the PDF exporter uses built-in FPDF2 fonts (Helvetica), which do not support all Unicode characters. Non-latin-1 characters are replaced.
- **No user accounts or history** — generated comics and PDFs are stored in `static/panels/` and `static/exports/` but are not linked to any session or user.
- **No content moderation** — the app passes user prompts directly to Gemini. Gemini's own safety filters apply, but no additional moderation layer is implemented.
- **Windows path handling** — image path resolution includes Windows-specific normalization; deployments on Linux should work correctly due to the multi-strategy path resolver in `exporters.py`.

---

## 🚀 Future Enhancements

- **Variable panel count** — allow the user to choose between 3, 4, 5, or 6 panels
- **Local image generation** — support locally hosted Stable Diffusion (e.g. via `diffusers`) as an alternative to HF hosted inference
- **Editable panels** — allow users to regenerate or edit individual panels without regenerating the entire comic
- **Style templates** — pre-built art style presets (Manga, Noir, Watercolor, Retro)
- **Comic bubble overlay** — render dialogue as actual speech bubbles overlaid on panel images
- **Session history** — store generated comics per browser session with a gallery view
- **Social sharing** — share a comic preview via a unique public URL
- **Multiple PDF layouts** — choose between single-panel-per-page and grid layouts
- **Background queue** — move generation to a background task queue so the HTTP request returns immediately with a job ID

---

## 📄 License

This project is provided for educational and demonstration purposes.

---

*Built with FastAPI · Google Gemini · Hugging Face · FPDF2 · Pillow*
