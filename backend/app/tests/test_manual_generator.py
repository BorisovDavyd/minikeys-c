import pytest

from app.generators.manual_allure_codegen import ManualTestGenerator
from sample_inputs import SAMPLE_UI, SAMPLE_YAML


@pytest.mark.asyncio
async def test_generate_ui_manual_tests():
    gen = ManualTestGenerator()
    files, summary = await gen.generate("ui", text=SAMPLE_UI, openapi_yaml=None, meta={})
    assert files[0]["path"].endswith("test_manual_generated.py")
    assert "PriceCalculatorUITests" in files[0]["content"]
    assert files[0]["content"].count("class PriceCalculatorUITests") >= 25


@pytest.mark.asyncio
async def test_generate_openapi_manual_tests():
    gen = ManualTestGenerator()
    files, _ = await gen.generate("openapi", text=None, openapi_yaml=SAMPLE_YAML, meta={})
    assert "EvolutionComputeAPITests" in files[0]["content"]
    assert files[0]["content"].count("class EvolutionComputeAPITests") >= 25
