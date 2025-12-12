from __future__ import annotations
import pytest

from app.validators.allure_standard_validator import AllureValidator


@pytest.mark.asyncio
async def test_validator_passes_valid_content():
    content = """
    @allure.manual
    @allure.label("owner", "qa")
    @allure.feature("feat")
    @allure.story("story")
    @allure.suite("suite")
    @mark.manual
    def test_sample():
        with allure.step("Arrange: setup"):
            pass
        with allure.step("Act: do"):
            pass
        with allure.step("Assert: check"):
            pass
    """
    validator = AllureValidator()
    report = await validator.validate([{ "path": "t.py", "content": content }])
    assert report["passed"] is True
    assert report["issues"] == []
    assert report["llm_feedback"] is not None


@pytest.mark.asyncio
async def test_validator_detects_missing():
    validator = AllureValidator()
    report = await validator.validate([{ "path": "bad.py", "content": "def test(): pass" }])
    assert report["passed"] is False
    assert len(report["issues"]) >= 1
