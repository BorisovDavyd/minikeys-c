from __future__ import annotations
from typing import List, Dict, Any, Tuple
import textwrap
import asyncio

from app.llm.cloudru_client import CloudRUClient
from app.parsers.ui_requirements import parse_ui_requirements
from app.parsers.openapi_parser import OpenAPIParser
from app.utils.errors import GenerationError


DEFAULT_META = {
    "owner": "qa-team",
    "feature": "TestOps Copilot",
    "story": "Generation",
    "suite": "manual",
    "priority": "high",
}


class ManualTestGenerator:
    def __init__(self, llm_client: CloudRUClient | None = None) -> None:
        self.llm = llm_client or CloudRUClient()

    async def generate(
        self, source_type: str, text: str | None, openapi_yaml: str | None, meta: Dict[str, Any]
    ) -> Tuple[List[Dict[str, str]], str]:
        meta_payload = {**DEFAULT_META, **(meta or {})}
        if source_type == "ui" and text:
            tests = await self._generate_from_ui(text, meta_payload)
        elif source_type == "openapi" and openapi_yaml:
            tests = await self._generate_from_openapi(openapi_yaml, meta_payload)
        else:
            raise GenerationError("Invalid source_type or missing input data")
        files = [{"path": "tests/manual/test_manual_generated.py", "content": tests}]
        summary = f"Generated manual tests from {source_type} input via Cloud.ru Evolution"
        return files, summary

    def _header(self) -> str:
        return textwrap.dedent(
            """
            import allure
            import pytest
            from pytest import mark


            allure_step = allure.step
            """
        )

    def _format_test(
        self,
        class_name: str,
        test_title: str,
        tag: str,
        priority: str,
        arrange: str,
        act: str,
        assertion: str,
        meta: Dict[str, Any],
    ) -> str:
        snake = test_title.lower().replace(" ", "_").replace("-", "_")
        return textwrap.dedent(
            f"""
            @allure.manual
            @allure.label("owner", "{meta['owner']}")
            @allure.feature("{meta['feature']}")
            @allure.story("{meta['story']}")
            @allure.suite("manual")
            @mark.manual
            class {class_name}:
                @allure.title("{test_title}")
                @allure.link("https://example.testops", name="ref")
                @allure.tag("{tag}")
                @allure.label("priority", "{priority}")
                def test_{snake}(self) -> None:
                    with allure_step("Arrange: {arrange}"):
                        pass
                    with allure_step("Act: {act}"):
                        pass
                    with allure_step("Assert: {assertion}"):
                        pass
            """
        )

    async def _llm_scenarios(self, prompt: str, fallback: List[str], count: int) -> List[str]:
        try:
            response = await self.llm.generate(prompt)
            candidates = [ln.strip("- ") for ln in response.splitlines() if ln.strip()]
        except Exception:
            candidates = []
        if not candidates:
            candidates = fallback or ["Scenario"]
        while len(candidates) < count:
            candidates.extend(fallback or candidates)
        return candidates[:count]

    async def _generate_from_ui(self, text: str, meta: Dict[str, Any]) -> str:
        requirements = parse_ui_requirements(text)
        tests_needed = max(25, len(requirements))
        llm_prompt = (
            "Generate concise UI test scenario titles for a price calculator application based on the following requirements. "
            "Return one scenario per line without numbering.\n" + text
        )
        scenarios = await self._llm_scenarios(llm_prompt, requirements, tests_needed)
        header = self._header()
        body_parts = []
        for idx in range(tests_needed):
            req = scenarios[idx]
            body_parts.append(
                self._format_test(
                    class_name="PriceCalculatorUITests",
                    test_title=f"UI - {req[:50]}",
                    tag="CRITICAL" if idx < 10 else "NORMAL",
                    priority="P1" if idx < 10 else "P2",
                    arrange="Navigate to price calculator and ensure clean state",
                    act=req,
                    assertion="Expected UI feedback aligns with requirement",
                    meta=meta,
                )
            )
        return header + "\n".join(body_parts)

    async def _generate_from_openapi(self, yaml_text: str, meta: Dict[str, Any]) -> str:
        parser = OpenAPIParser(yaml_text)
        operations = parser.operations()
        if not operations:
            raise GenerationError("OpenAPI spec contained no operations")
        tests_needed = max(25, len(operations))
        op_descriptions = "\n".join(f"- {op['method']} {op['path']}" for op in operations)
        llm_prompt = (
            "Produce API test scenario names for Evolution Compute endpoints. Return one per line based on these operations:\n"
            f"{op_descriptions}"
        )
        scenarios = await self._llm_scenarios(llm_prompt, [op.get("summary") or op["path"] for op in operations], tests_needed)
        header = self._header()
        body_parts = []
        for idx in range(tests_needed):
            op = operations[idx % len(operations)]
            scenario_title = scenarios[idx]
            body_parts.append(
                self._format_test(
                    class_name="EvolutionComputeAPITests",
                    test_title=f"API - {scenario_title[:50]}",
                    tag="CRITICAL" if idx < 10 else "NORMAL",
                    priority="P1" if idx < 10 else "P2",
                    arrange="Prepare authorized client and payload",
                    act=f"Call {op['method']} {op['path']}",
                    assertion="Validate response status and schema",
                    meta=meta,
                )
            )
        return header + "\n".join(body_parts)
