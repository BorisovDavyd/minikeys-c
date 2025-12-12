from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAMPLE_UI = (ROOT / "ui_requirements.md").read_text()
SAMPLE_YAML = (ROOT / "openapi_sample.yaml").read_text()
