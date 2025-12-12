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
- `CLOUDRU_API_KEY` / `CLOUDRU_BASE_URL` – Cloud.ru Evolution API (if not using mock)
- `MOCK_LLM` – set to `1` (default) to use deterministic stub
- `GITLAB_TOKEN`, `GITLAB_BASE_URL` – enable GitLab integration
- `UI_BASE_URL`, `API_BASE_URL`, `userPlaneApiToken` – used by generated tests
- `VITE_BACKEND_URL` – frontend backend URL

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
