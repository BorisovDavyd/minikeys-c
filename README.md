# TestOps Copilot

Agentic system that generates Allure TestOps as Code manual tests, UI and API automated tests, validates standards, and provides optimization hints. Backend uses FastAPI; frontend uses React + Vite.

## Features
- Manual test generation from UI requirements or OpenAPI (Allure decorators, AAA steps, 25+ cases)
- Automated Playwright + pytest UI skeletons
- Automated pytest API tests from OpenAPI
- Validation of Allure structure (with Cloud.ru Evolution narrative feedback via the official client wrapper)
- Optional optimizer (duplicate detection, plan suggestions) enriched by Cloud.ru Evolution feedback
- Mock LLM mode by default

## Setup
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## Environment Variables
- `CLOUDRU_API_KEY` / `CLOUDRU_BASE_URL` – Cloud.ru Foundation Models OpenAI-compatible API key and optional base URL (default `https://foundation-models.api.cloud.ru`)
- `CLOUDRU_MODEL` – model id for Foundation Models (default `gpt-4o-mini`)
- `MOCK_LLM` – set to `1` (default) to use deterministic stub
- `GITLAB_TOKEN`, `GITLAB_BASE_URL` – enable GitLab integration
- `UI_BASE_URL`, `API_BASE_URL`, `userPlaneApiToken` – used by generated tests
- `VITE_BACKEND_URL` – frontend backend URL

### Which API key is required?
Use an API key from the **Cloud.ru Foundation Models** service (OpenAI-compatible endpoint described at https://cloud.ru/docs/foundation-models/ug/topics/api-ref). Other service keys (monitoring, audit, notifications, logging, AI Agents, etc.) will not work for LLM generation.

To call the real model instead of the deterministic mock, set for example:
```bash
export CLOUDRU_API_KEY="<your_foundation_models_api_key>"
export CLOUDRU_BASE_URL="https://foundation-models.api.cloud.ru"  # default
export CLOUDRU_MODEL="gpt-4o-mini"  # or another available model id
export MOCK_LLM=0
```

## Running (dev)
Backend:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Frontend:
```bash
cd frontend
npm run dev -- --host
```

Swagger UI available at `http://localhost:8000/docs`.

## Docker Compose
```bash
docker-compose build
docker-compose up
```

## Tests
Run backend tests with coverage:
```bash
cd backend
pytest --cov=app --cov=sample_inputs --cov-report=term-missing
```

## Sample Generation
Manual from UI requirements:
```bash
curl -X POST http://localhost:8000/api/generate/manual \
  -H "Content-Type: application/json" \
  -d @<(cat <<'PAYLOAD'
{
  "source_type": "ui",
  "text": "$(cat ../sample_inputs/ui_requirements.md)"
}
PAYLOAD
)
```
Manual from OpenAPI:
```bash
curl -X POST http://localhost:8000/api/generate/manual \
  -H "Content-Type: application/json" \
  -d "{\"source_type\":\"openapi\",\"openapi_yaml\":\"$(cat ../sample_inputs/openapi_sample.yaml | sed 's/\\/\\\\/g' | tr '\n' ' ')\"}"
```

## Project Structure
- `backend/` FastAPI app, generators, validators, tests
- `frontend/` React UI
- `sample_inputs/` Example UI requirements and OpenAPI spec
