# AI Content Factory – Developer Guide

This repo hosts an AI-powered content generation platform with a FastAPI backend and a lightweight HTML/CSS/JS frontend. It integrates an Ollama-hosted LLM, ChromaDB for brand voice retrieval, and a metrics system for quality tracking.

## Quick Start

- Requirements:
	- Python 3.11+ (project currently uses a venv)
	- `uv` (optional, for fast installs)
	- Ollama running locally with an installed model (e.g., `qwen2.5:7b`)

- Setup:
	- Create/activate venv and install deps
		- If using `uv`:
			```powershell
			uv sync
			```
		- Or standard pip:
			```powershell
			python -m venv .venv; & .\.venv\Scripts\Activate.ps1
			pip install -e .
			pip install fastapi "uvicorn[standard]"
			```

- Run the web UI:
	```powershell
	& .\.venv\Scripts\Activate.ps1; python run_web_ui.py
	```
	- UI: `http://localhost:8000`
	- API docs: `http://localhost:8000/docs`

## Project Structure

```
src/ai_content_factory/
	agents/                # ContentWriterAgent (LangGraph workflow)
	api/                   # FastAPI app + static frontend
		app.py               # API endpoints
		static/              # index.html, styles.css, app.js
	core/
		metrics.py           # ContentMetrics + evaluator
		metrics_logger.py    # Persistence of metrics
	database/
		chroma_manager.py    # ChromaDB wrapper
	llm/
		ollama_provider.py   # LLM provider wrapper
	config/                # Pydantic config + YAML
outputs/                 # Generated markdown exports
metrics_logs/            # Historical metrics (json/csv)
```

## Architecture Overview

- Backend: FastAPI (`src/ai_content_factory/api/app.py`)
	- 13+ REST endpoints for content generation, status, library CRUD, analytics, and settings
	- Serves static frontend from `api/static`
	- Aggregates metrics from `metrics_logs/metrics_history.json`

- Frontend: Vanilla HTML/CSS/JS
	- Single-page UI (`index.html`) with tabs: Dashboard, Create, Library, Analytics, Settings
	- Chart.js used for visualizations
	- `app.js` integrates with backend endpoints

- Content Generation: `ContentWriterAgent`
	- LangGraph workflow: retrieve brand voice → outline → intro → sections (loop) → conclusion → CTA → assemble → SEO optimize
	- Inputs accepted by `generate_article(...)`: `topic`, `target_keyword`, `target_word_count`, `target_audience`, `content_type`
	- Brand voice retrieved semantically from ChromaDB collections defined in config

- Metrics: `ContentMetricsEvaluator`
	- Calculates: quality, brand voice similarity, keyword density, readability, word count accuracy, heading structure, SEO requirements, generation time
	- Persisted via `MetricsLogger` to `metrics_logs/metrics_history.json`

## Key Endpoints

- `POST /api/content/generate` → starts background generation task
- `GET /api/content/status/{task_id}` → retrieves task progress
- `GET /api/content/library` → list generated content
- `GET /api/content/{content_id}` → fetch content details
- `DELETE /api/content/{content_id}` → delete content and file
- `PUT /api/content/{content_id}/status` → update status (`draft|review|published`)
- `GET /api/analytics/dashboard` → KPIs and aggregated metrics
- `GET /api/settings` / `PUT /api/settings` → config surface

## Developer Workflows

- Frontend changes:
	- Edit `src/ai_content_factory/api/static/index.html`, `styles.css`, `app.js`
	- The server runs with `reload=True`, so refresh the browser after edits

- Backend changes:
	- Edit `src/ai_content_factory/api/app.py`
	- Add new endpoints or extend analytics safely; validate with `http://localhost:8000/docs`

- Agent changes:
	- Update `src/ai_content_factory/agents/content_writer_agent.py`
	- Keep prompts aligned with metrics expectations (short sentences, keyword density)

## Configuration

- `src/ai_content_factory/config/config.yaml` controls model and DB settings
- Accessed via `load_config()` (Pydantic models); prefer attribute access over dict-like `.get()`

## Data & Persistence

- Content Library: `outputs/content_library.json` (list of items)
	- Each item includes: `id`, `title`, `status`, `date`, `topic`, `keyword`, `word_count`, `content`, `meta_description`, `metrics`

- Metrics History: `metrics_logs/metrics_history.json`
	- Aggregated on the dashboard/analytics
	- Advanced analytics include pass-rate computed from available metrics only

## Common Dev Tasks

- Add a new metric:
	- Extend `ContentMetrics` in `metrics.py`
	- Compute in `ContentMetricsEvaluator`
	- Persist via `MetricsLogger`
	- Surface in `/api/analytics/dashboard` and consume in `app.js`

- Add UI widgets:
	- Create HTML in `index.html`
	- Style in `styles.css`
	- Wire API calls in `app.js`

## Testing & Validation

- Python tests (examples under `tests/`):
	```powershell
	& .\.venv\Scripts\Activate.ps1; pytest -q
	```

- Manual validation:
	- Generate content in UI, observe progress modal
	- Check `outputs/*.md` and `outputs/content_library.json`
	- Analytics should reflect metrics from `metrics_logs/metrics_history.json`

## Troubleshooting

- `No module named uvicorn`: Ensure virtual environment is active and `uvicorn` installed.
- Brand voice not found: Ensure ChromaDB collections exist (see `scripts/load_brand_voice.py`). if not, run generate_brand_embeddings.py and it'll create the embeddings for you. the data is already in the repo(brand_voice_sample.json contains 100 samples).


