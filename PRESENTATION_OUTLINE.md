# 📊 ComicCraft — Project Presentation Outline
### AI Comic Story Creator | College / Academic Presentation Guide

---

> **Suggested total duration:** 12–15 minutes presentation + 3–5 minutes Q&A  
> **Each slide heading below = one presentation slide**

---

## SLIDE 1 — Title Slide

**ComicCraft: AI Comic Story Creator**

> *Transforming a text idea into a five-panel illustrated comic using Google Gemini and Hugging Face*

- Your Name / Team Names
- Department / Institution
- Course / Subject
- Date

---

## SLIDE 2 — Introduction

**What is ComicCraft?**

ComicCraft is a web-based Generative AI application that allows any user — regardless of artistic or writing skill — to produce a complete five-panel illustrated comic story from a single text prompt.

The user provides:
- A story idea
- A character name
- A setting
- A tone (e.g. Adventurous, Funny)
- An art style (e.g. Comic Book, Watercolor)

The system returns:
- A structured five-panel narrative (caption, narration, dialogue per panel)
- One AI-generated illustration per panel
- A downloadable PDF comic book

**Key point:** The entire creative process — writing, illustrating, and formatting — is handled by AI.

---

## SLIDE 3 — Problem Statement

**The Gap in Accessible Creative Storytelling**

Creating a comic story traditionally requires:

| Requirement | Barrier |
|---|---|
| Story writing | Strong narrative and creative writing skills |
| Character design | Illustration or digital art expertise |
| Panel layout | Knowledge of comic book composition |
| Publishing | Desktop publishing or professional software |

**Consequence:** The comic medium is inaccessible to most people who have an idea but lack the technical skills to execute it.

**What is missing:** A simple, intelligent tool that bridges the gap between an idea and a finished, shareable comic — without requiring any artistic ability from the user.

---

## SLIDE 4 — Existing System

**How Comics Are Created Today**

| Method | Tool | Limitations |
|---|---|---|
| Manual creation | Illustrator, Photoshop | Requires artistic skill; time-consuming |
| Comic builders | Canva, Pixton | Clip-art only; no original story generation |
| ChatGPT prompting | OpenAI ChatGPT | Text story only; no image pipeline; no PDF |
| Image-only AI | Midjourney, DALL·E | Generates images but no narrative structure |
| Comic script tools | Celtx, FadeIn | Script formatting only; no image or PDF output |

**None of the existing tools provide an end-to-end pipeline:**
Text idea → Structured story → AI images → Layout → PDF

---

## SLIDE 5 — Proposed System

**ComicCraft: End-to-End AI Comic Pipeline**

ComicCraft solves the identified gap by providing:

1. **Structured story generation** using Google Gemini (five-panel outline + full script)
2. **Automated image generation** using Hugging Face hosted text-to-image inference
3. **Strict pipeline validation** — exactly 5 panels, 5 images, always
4. **HTML preview** rendered in the browser immediately after generation
5. **PDF export** — downloadable, shareable comic book in A4 format
6. **Graceful fallback** — the pipeline always completes even if image generation fails

**Target users:** Students, educators, hobbyists, content creators, anyone with a story idea

---

## SLIDE 6 — Project Objectives

1. **Story Generation:** Use Google Gemini to produce a coherent, five-panel comic outline and expand it into a full script with captions, narration, and dialogue
2. **Image Generation:** Use Hugging Face hosted inference to generate one AI illustration per panel
3. **5-Panel Validation:** Enforce that the output always contains exactly 5 panels with 5 matching images
4. **Comic Preview:** Render a browser-based comic preview page immediately after generation
5. **PDF Export:** Generate a professionally formatted, downloadable A4 PDF comic
6. **Resilience:** Ensure the application never crashes due to external API failures — fallback at every layer
7. **Accessibility:** Require no user artistic or writing skill — only a story idea

---

## SLIDE 7 — System Architecture

**Architecture Overview**

```
[User Browser]
      │
      │  HTTP POST (form or JSON)
      ▼
[FastAPI — routes.py]
      │
      ├──► [gemini_flash.py]  →  Google Gemini API
      │         Returns: ComicOutline (5 PanelOutline)
      │
      ├──► [gemini_pro.py]  →  Google Gemini API
      │         Returns: ComicStory (5 PanelStory)
      │
      ├──► [image_generator.py]  →  Hugging Face API (×5)
      │         Returns: 5 PNG image paths
      │         Fallback: Pillow placeholder images
      │
      ├──► [layout_builder.py]
      │         Validates: 5 panels + 5 images
      │         Returns: List[ComicPanel]
      │
      └──► [exporters.py]  →  FPDF2
                Returns: comiccraft_<timestamp>.pdf

[Jinja2 Templates]  →  comic_preview.html (browser)
[StaticFiles]       →  /static/panels/, /static/exports/
```

**Design pattern:** Linear pipeline with validation checkpoints at each stage.

---

## SLIDE 8 — Technologies Used

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.11 | Core application |
| Web Framework | FastAPI | HTTP routing, form handling, JSON API, auto-docs |
| ASGI Server | Uvicorn | Production-grade async web server |
| Templates | Jinja2 | Server-side HTML rendering |
| AI — Text | Google Gemini (`google-genai`) | Story outline and script generation |
| AI — Images | Hugging Face (`huggingface-hub`) | Text-to-image panel illustration |
| Data Validation | Pydantic + pydantic-settings | Request models, structured output, config |
| PDF Generation | FPDF2 | A4 comic PDF export |
| Image Processing | Pillow (PIL) | Fallback panel image creation |
| Environment | python-dotenv | Secure `.env` configuration |
| Frontend | HTML + CSS + JavaScript | Web form, loading state, preview layout |
| Testing | pytest + httpx | Automated test suite |

---

## SLIDE 9 — Module Description

The application is split into focused single-responsibility modules:

| Module | File | Responsibility |
|---|---|---|
| **Config** | `app/config.py` | Loads settings from `.env` using pydantic-settings; creates output directories |
| **Models** | `app/models.py` | Defines all Pydantic data models (request, outline, story, panel, response) |
| **Routes** | `app/routes.py` | All FastAPI HTTP endpoints; orchestrates the generation pipeline |
| **Gemini Client** | `app/gemini_client.py` | Low-level Gemini API calls; fallback chain; friendly error messages |
| **Gemini Flash** | `app/gemini_flash.py` | Generates structured `ComicOutline` (5 `PanelOutline` objects) |
| **Gemini Pro** | `app/gemini_pro.py` | Expands outline into full `ComicStory` (5 `PanelStory` objects) |
| **Image Generator** | `app/image_generator.py` | HF inference calls; two-tier fallback to Pillow placeholders |
| **Layout Builder** | `app/layout_builder.py` | Validates 5-panel + 5-image constraint; assembles `List[ComicPanel]` |
| **Exporters** | `app/exporters.py` | FPDF2-based A4 PDF generation; Windows-safe image path resolution |
| **Main** | `app/main.py` | FastAPI app factory; static file mount; health endpoint |

---

## SLIDE 10 — AI Workflow

**Two-Stage Gemini Generation Pipeline**

**Stage 1 — Outline Generation (`gemini_flash.py`)**

Input: `story_prompt`, `character_name`, `setting`, `tone`, `art_style`

Gemini is prompted to return **structured JSON** matching the `ComicOutline` schema:
```
ComicOutline
  └── panels: List[PanelOutline] (exactly 5)
        ├── panel_number
        ├── title
        ├── scene_description
        └── image_prompt
```
Validation: raises `RuntimeError` if panel count ≠ 5.

---

**Stage 2 — Story Expansion (`gemini_pro.py`)**

Input: `ComicOutline` JSON + `character_name` + `tone`

Gemini expands each panel into a full `ComicStory` schema:
```
ComicStory
  └── panels: List[PanelStory] (exactly 5)
        ├── panel_number, title, scene_description, image_prompt
        ├── caption        ← NEW
        ├── narration      ← NEW
        └── dialogue       ← NEW (optional)
```
Validation: raises `RuntimeError` if panel count ≠ 5.

**Gemini uses structured output mode** (`response_mime_type="application/json"`) so the response is directly parsed by Pydantic — no regex or text parsing required.

---

## SLIDE 11 — Backend

**FastAPI Routes**

| Endpoint | Method | Type | Description |
|---|---|---|---|
| `/` | GET | HTML | Home page — story form |
| `/generate` | POST | HTML form | Full comic pipeline → `comic_preview.html` |
| `/generate-comic/json` | POST | JSON API | Same pipeline → `GenerateResponse` JSON |
| `/download/{filename}` | GET | File | PDF download with path-traversal protection |
| `/test-image` | GET | JSON | Standalone image generation test |
| `/health` | GET | JSON | Service liveness check |
| `/export-success` | GET | HTML | Export confirmation page |
| `/docs` | GET | HTML | Auto-generated Swagger UI |

**Request validation** is handled by Pydantic's `PromptRequest` model:
- `story_prompt`: 3–2000 characters
- `character_name`: 1–80 characters
- `setting`: 1–120 characters
- `tone`: 1–60 characters
- `art_style`: 1–80 characters

---

## SLIDE 12 — Frontend

**Web Interface (HTML + CSS + JavaScript)**

**Home page (`index.html`):**
- Styled input form for all 5 generation parameters
- Client-side form validation (empty field detection)
- Loading spinner activates on form submission
- Error messages displayed inline if generation fails

**Comic preview page (`comic_preview.html`):**
- Renders all 5 panels in a comic-strip layout
- Each panel: title → image → caption → narration → dialogue
- "Download PDF" button links to `/download/<filename>`
- Responsive layout for different screen sizes

**Styling (`static/css/style.css`):**
- Dark-themed comic aesthetic
- Animated loading states
- Panel card layout with hover effects

**No JavaScript framework is used** — the frontend is plain HTML, CSS, and vanilla JS. All rendering is server-side (Jinja2).

---

## SLIDE 13 — Image Generation

**Hugging Face Hosted Inference**

Each of the 5 `image_prompt` strings from the story pipeline is sent to Hugging Face's `InferenceClient`:

```
Panel image_prompt  →  InferenceClient.text_to_image()
                    →  PIL Image  →  PNG saved to static/panels/
                    →  Web path returned: /static/panels/<filename>
```

**Default model:** `stabilityai/stable-diffusion-3-medium-diffusers`  
**Image dimensions:** 768 × 1024 pixels (portrait, comic panel ratio)  
**Inference steps:** 28

**Two-tier fallback system:**

```
Tier 1: Try primary HF model
   ↓ (fail)
Tier 2: Try each model in HF_FALLBACK_MODELS list
   ↓ (all fail OR HF_TOKEN not configured)
Tier 3: Generate styled Pillow placeholder image locally
```

The placeholder image maintains the comic aesthetic (dark background, panel badge, prompt summary, comic frame border) so the preview and PDF always render correctly.

---

## SLIDE 14 — PDF Generation

**FPDF2 — Server-Side PDF Export**

After the layout is assembled, `exporters.save_pdf()` generates an A4 PDF:

**Structure per panel (one page per panel):**

```
Page (A4 Portrait, 210mm × 297mm)
├── Panel title heading        (Helvetica Bold 18pt)
├── Panel image                (160mm wide, centered, y=30mm)
├── Scene description          (Helvetica Italic 10pt)
├── Caption label + text       (Helvetica Bold 11pt / Regular 10pt)
├── Narration label + text     (Helvetica Bold 11pt / Regular 10pt)
└── Dialogue label + text      (if dialogue is non-empty)
```

**Windows-safe path resolution (`_resolve_image_path`):**  
Handles `/static/panels/`, `static/panels/`, and direct file paths across platforms.

**Font encoding:** Non-latin-1 characters are replaced (FPDF2 limitation with built-in fonts).

**Security:** PDF filenames are validated against the `static/exports/` directory — path traversal is blocked at the download endpoint.

---

## SLIDE 15 — Testing

**pytest Test Suite (`tests/test_core.py`)**

| Test | What is verified |
|---|---|
| `test_layout_builder_validates_five_panels` | 5 panels + 5 images → correct `List[ComicPanel]` |
| `test_layout_builder_rejects_non_five_panels` | 4 panels → `ValueError` with correct message |
| `test_layout_builder_rejects_mismatched_images` | 5 panels + 4 images → `ValueError` |
| `test_pdf_export_and_path_resolution` | Full pipeline: placeholder images → layout → PDF saved to disk; file size > 1000 bytes |

**Test strategy:**
- All tests run **offline** — no real API credentials required
- `generate_image()` automatically uses the Pillow fallback when `HF_TOKEN` is absent
- PDF generation is tested end-to-end against the filesystem
- Layout validation logic is tested with boundary conditions

**Run tests:**
```bash
pytest -v
# Result: 4 passed in ~0.6 seconds
```

---

## SLIDE 16 — Results

**Demonstrated Outcomes**

| Metric | Result |
|---|---|
| Story generation (Gemini) | Coherent 5-panel narrative in ~5–15 seconds |
| Image generation (HF) | 5 illustrated panels in ~30–90 seconds |
| Fallback availability | 100% — pipeline always completes |
| 5-panel validation | Enforced at outline, story, layout, and PDF stages |
| PDF export | A4 multi-page PDF generated in < 1 second |
| Test suite | 4/4 tests passing |
| API documentation | Auto-generated Swagger UI at `/docs` |
| Endpoint security | Path traversal protection on PDF download |

**Live demo:** Submit a prompt → observe Gemini generation → view 5-panel preview → download PDF → show Swagger docs

---

## SLIDE 17 — Limitations

| Limitation | Impact |
|---|---|
| **Fixed 5-panel output** | Variable panel counts are not supported |
| **Gemini structured output dependency** | Rare malformed JSON responses can cause generation failure |
| **HF inference latency** | 30–90 seconds for image generation; free tier has strict rate limits |
| **PDF font encoding** | Non-latin-1 (non-Western) characters are replaced in PDF |
| **No session or history** | Generated comics are not linked to users or sessions |
| **No content moderation layer** | Relies entirely on Gemini's built-in safety filters |
| **No background queue** | The HTTP request blocks until all 5 images are generated |
| **Windows path specifics** | Path resolver includes Windows normalization logic |

---

## SLIDE 18 — Future Enhancements

| Enhancement | Description |
|---|---|
| **Variable panel count** | Allow 3, 4, 5, or 6 panels selected by the user |
| **Local image generation** | Support offline Stable Diffusion via `diffusers` |
| **Panel regeneration** | Regenerate a single panel without rerunning the full pipeline |
| **Art style presets** | Pre-built styles: Manga, Noir, Watercolor, Retro, Superhero |
| **Speech bubble overlay** | Render dialogue as actual speech bubbles on panel images |
| **Background task queue** | Use async tasks so the browser does not block during generation |
| **Session history & gallery** | Store and browse past comics per user session |
| **Social sharing** | Generate a shareable public URL for a comic |
| **Multiple PDF layouts** | Grid layout (all 5 panels on one page) vs. one-per-page |
| **User accounts** | Authentication and personal comic library |

---

## SLIDE 19 — Conclusion

**Summary**

ComicCraft demonstrates a complete, end-to-end Generative AI pipeline built on modern Python technologies:

- **Google Gemini** provides structured narrative intelligence — producing story outlines and scripts that are directly parsed as typed Pydantic objects
- **Hugging Face Inference** provides text-to-image generation at scale, with graceful degradation when unavailable
- **FastAPI** delivers a production-grade web application with auto-generated documentation, strict input validation, and file security
- **FPDF2 + Pillow** handle all media generation server-side with no external services
- **A resilient design philosophy** ensures the application never crashes due to external API failures

**Key takeaway:** ComicCraft shows how multiple AI services can be composed into a reliable, user-friendly product through careful pipeline design, validation, and fallback handling — principles that apply directly to production Generative AI systems.

---

## SLIDE 20 — Q&A / References

**References**

- Google Gemini API — https://aistudio.google.com/
- Hugging Face Inference API — https://huggingface.co/inference-api
- FastAPI Documentation — https://fastapi.tiangolo.com/
- FPDF2 Documentation — https://py-pydantic.github.io/fpdf2/
- Pydantic Documentation — https://docs.pydantic.dev/
- Stable Diffusion 3 — https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers

**Project repository structure:**
```
ComicCraft/
├── app/          ← Backend pipeline (FastAPI + Gemini + HF + FPDF2)
├── templates/    ← Jinja2 HTML templates
├── static/       ← CSS, generated images, generated PDFs
├── tests/        ← pytest test suite
├── README.md     ← Full project documentation
└── DEMO_CHECKLIST.md  ← This demo guide
```

---

*ComicCraft — AI Comic Story Creator | Project Presentation*
