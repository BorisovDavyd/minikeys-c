from __future__ import annotations
from typing import List, Dict, Any, Tuple
import textwrap

from app.llm.cloudru_client import CloudRUClient
from app.parsers.ui_requirements import parse_ui_requirements


class AutoUiGenerator:
    def __init__(self, llm_client: CloudRUClient | None = None) -> None:
        self.llm = llm_client or CloudRUClient()

    async def generate(
        self, requirements_text: str, manual_tests: List[Dict[str, str]], base_url: str | None
    ) -> Tuple[List[Dict[str, str]], str]:
        requirements = parse_ui_requirements(requirements_text)
        tests_needed = max(5, len(requirements))
        prompt = (
            "Generate short UI e2e flow titles for Playwright based on price calculator requirements. "
            "One scenario per line without numbering.\n" + requirements_text
        )
        try:
            llm_response = await self.llm.generate(prompt)
            scenarios = [ln.strip("- ") for ln in llm_response.splitlines() if ln.strip()]
        except Exception:
            scenarios = []
        if not scenarios:
            scenarios = requirements or ["Open landing page"]
        while len(scenarios) < tests_needed:
            scenarios.extend(scenarios)
        scenarios = scenarios[:tests_needed]

        header = textwrap.dedent(
            """
            import os
            import pytest
            from playwright.sync_api import Page, expect


            BASE_URL = os.getenv("UI_BASE_URL", "http://localhost:3000")
            """
        )
        body_parts = []
        for idx in range(tests_needed):
            req = scenarios[idx]
            snake = req.lower().replace(" ", "_").replace("-", "_")
            body_parts.append(
                textwrap.dedent(
                    f"""
                    @pytest.mark.e2e
                    @pytest.mark.skipif(not BASE_URL, reason="Base URL not configured")
                    def test_ui_flow_{idx+1}_{snake}(page: Page):
                        page.goto(BASE_URL)
                        # Arrange
                        page.wait_for_timeout(100)
                        # Act
                        # {req}
                        # Assert
                        expect(page).to_have_url(BASE_URL)
                    """
                )
            )
        content = header + "\n".join(body_parts)
        files = [{"path": "tests/auto_ui/test_ui_generated.py", "content": content}]
        summary = "Generated Playwright pytest skeletons via Cloud.ru Evolution"
        return files, summary
