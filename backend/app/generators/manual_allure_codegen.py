from __future__ import annotations
from typing import List, Dict, Any, Tuple
import textwrap

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
    def generate(self, source_type: str, text: str | None, openapi_yaml: str | None, meta: Dict[str, Any]) -> Tuple[List[Dict[str, str]], str]:
        meta_payload = {**DEFAULT_META, **(meta or {})}
        if source_type == "ui" and text:
            tests = self._generate_from_ui(text, meta_payload)
        elif source_type == "openapi" and openapi_yaml:
            tests = self._generate_from_openapi(openapi_yaml, meta_payload)
        else:
            raise GenerationError("Invalid source_type or missing input data")
        files = [{"path": "tests/manual/test_manual_generated.py", "content": tests}]
        summary = f"Generated manual tests from {source_type} input"
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

    def _format_test(self, class_name: str, test_title: str, tag: str, priority: str, arrange: str, act: str, assertion: str, meta: Dict[str, Any]) -> str:
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

    def _generate_from_ui(self, text: str, meta: Dict[str, Any]) -> str:
        requirements = parse_ui_requirements(text)
        tests_needed = max(25, len(requirements))
        header = self._header()
        body_parts = []
        for idx in range(tests_needed):
            req = requirements[idx % len(requirements)] if requirements else f"UI scenario {idx+1}"
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

    def _generate_from_openapi(self, yaml_text: str, meta: Dict[str, Any]) -> str:
        parser = OpenAPIParser(yaml_text)
        operations = parser.operations()
        if not operations:
            raise GenerationError("OpenAPI spec contained no operations")
        tests_needed = max(25, len(operations))
        header = self._header()
        body_parts = []
        for idx in range(tests_needed):
            op = operations[idx % len(operations)]
            title = op.get("summary") or f"{op['method']} {op['path']}"
            body_parts.append(
                self._format_test(
                    class_name="EvolutionComputeAPITests",
                    test_title=f"API - {title}",
                    tag="CRITICAL" if idx < 10 else "NORMAL",
                    priority="P1" if idx < 10 else "P2",
                    arrange="Prepare authorized client and payload",
                    act=f"Call {op['method']} {op['path']}",
                    assertion="Validate response status and schema",
                    meta=meta,
                )
            )
        return header + "\n".join(body_parts)
