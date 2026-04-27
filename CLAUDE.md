# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
just bootstrap      # Install all dependencies + git hooks (run once after clone)
just dev            # Start backend dev server with auto-reload at http://127.0.0.1:8000
just check          # Run lint + format check + typecheck (all-in-one gate)
just lint           # Ruff lint only
just lint-fix       # Ruff lint with auto-fix
just fmt            # Ruff format
just typecheck      # Pyrefly type check
just test           # Run all tests
just test tests/test_routes.py::test_name  # Run a single test

# Frontend (Svelte + TypeScript)
just dev-frontend        # Vite dev server with HMR at http://localhost:5173 (run alongside just dev)
just build-frontend      # Build Svelte app into src/guess_explainr/static/app/
just check-frontend      # Type-check the frontend
just bootstrap-frontend  # Install frontend npm deps (included in just bootstrap)
```

Pre-commit hooks are managed by `prek` (see `prek.toml`), not standard pre-commit.

## Architecture

Guess Explainr is a single-user local web app that helps GeoGuessr players learn from past rounds. It fetches a Google Street View panorama, then uses an LLM (via pydantic-ai) to analyze the image against PlonkIt country guides bundled as PDFs.

### Backend

**Framework**: Litestar (ASGI), served by uvicorn.

**Entry point**: `src/guess_explainr/__main__.py` — starts uvicorn and opens a browser tab.

**App wiring** (`app.py`): Registers two routers from `routes/index.py` — a page router at `/` and an API router at `/api/`.

**State** (`state.py`):
- `InMemoryState` — a module-level singleton holding the current panorama ID and JPEG bytes. Single-user by design; no session isolation.
- `StateConfig` — persisted as JSON in the platform config dir (via `platformdirs`). Stores the LLM provider, model, API key, and optional Maps API key.

**AI** (`ai.py`): Builds a pydantic-ai `Agent` on each request using the saved config. Streams analysis via `stream_analysis()` which feeds the panorama image + relevant PlonkIt PDF guides as `BinaryContent` to the LLM.

**Model providers** (`model_provider.py`): `ModelProvider` enum wraps OpenAI, Anthropic, and Google via pydantic-ai provider/model pairs. Also fetches live model lists from each provider's API.

### Routes (4-step wizard)

All API routes return JSON. SSE endpoints stream Server-Sent Events.

| File | Path | Purpose |
|---|---|---|
| `routes/step1.py` | `/api/config`, `/api/models` | Save/load LLM config; fetch model list for a provider |
| `routes/step2.py` | `/api/process-url` | Parse a Google Maps URL, extract panorama ID + lat/lon, reverse-geocode to a country, trigger panorama download |
| `routes/step3.py` | `/api/compare` | Accept selected countries + user questions; return JSON with SSE stream URL |
| `routes/step4.py` | `/api/analysis-stream`, `/api/chat`, `/api/new-chat-id` | Stream AI analysis via SSE; stub chat endpoint |
| `routes/panorama.py` | `/api/panorama-image` | Serve cached panorama JPEG; handles download via official Maps Tiles API or scraping fallback |

### Frontend

**Framework**: Svelte 5 + TypeScript, built with Vite.

**Location**: `frontend/` directory at the repo root.

**Build output**: `src/guess_explainr/static/app/` (served by Litestar's static file handler).

**Dev workflow**: Run `just dev` (backend on port 8000) and `just dev-frontend` (Vite HMR on port 5173) in separate terminals. The Vite dev server proxies `/api` and `/static` to the backend.

**Component structure** (`frontend/src/`):
- `App.svelte` — root component; owns all wizard state; handles step transitions
- `components/StepIndicator.svelte` — step progress bar
- `components/Step1Config.svelte` — LLM provider/model/API key configuration
- `components/Step2Url.svelte` — Google Maps URL input
- `components/Step3Countries.svelte` — country selection + compare trigger
- `components/Step4Analysis.svelte` — SSE streaming analysis + chat

**API layer** (`frontend/src/lib/`):
- `api.ts` — typed fetch wrappers for every backend endpoint
- `sse.ts` — reusable `EventSource` helper (`connectSSE`)

**Styling**: DaisyUI 5 + Tailwind CSS via CDN (in `frontend/index.html`). The `prose.css` in `static/` provides typography styles for rendered markdown from SSE events.

**SSE rendering**: Analysis stream events send rendered HTML. Svelte renders it via `{@html}` — equivalent to the previous HTMX `hx-swap="innerHTML"`.

### Static assets

`src/guess_explainr/static/files/plonkit/` — PlonkIt community guides as PDFs, one per country slug (e.g. `france.pdf`). These are loaded at analysis time and passed directly to the LLM as `BinaryContent`. The `fetch_plonkit.py` script regenerates these (requires Docker + weasyprint).

### Testing

Tests use `litestar.testing.TestClient`. The `conftest.py` fixture resets `InMemoryState` around every test. For route tests, monkeypatching `state._config_file` to a `tmp_path` isolates config on disk.
