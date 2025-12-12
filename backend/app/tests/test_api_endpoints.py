from fastapi.testclient import TestClient
from app.main import app
from sample_inputs import SAMPLE_UI, SAMPLE_YAML


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_generate_manual_ui():
    resp = client.post("/api/generate/manual", json={"source_type": "ui", "text": SAMPLE_UI, "meta": {"owner": "qa"}})
    assert resp.status_code == 200
    data = resp.json()
    assert "files" in data and len(data["files"]) == 1


def test_validate_endpoint():
    manual_resp = client.post("/api/generate/manual", json={"source_type": "ui", "text": SAMPLE_UI})
    files = manual_resp.json()["files"]
    resp = client.post("/api/validate", json={"manual_tests": files})
    assert resp.status_code == 200
    assert "report" in resp.json()


def test_auto_api_generation():
    resp = client.post("/api/generate/auto/api", json={"openapi_yaml": SAMPLE_YAML, "base_url": "http://localhost", "auth": {}})
    assert resp.status_code == 200
    assert resp.json()["files"]
