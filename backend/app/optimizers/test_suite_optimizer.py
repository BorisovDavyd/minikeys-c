from __future__ import annotations
from typing import List, Dict, Any
import hashlib

from app.llm.cloudru_client import CloudRUClient


class TestSuiteOptimizer:
    def __init__(self, llm_client: CloudRUClient | None = None) -> None:
        self.llm = llm_client or CloudRUClient()

    async def optimize(self, manual_tests: List[Dict[str, str]], requirements_text: str | None, openapi_yaml: str | None) -> Dict[str, Any]:
        seen = {}
        duplicates = []
        for test in manual_tests:
            content = test.get("content", "")
            digest = hashlib.md5(content.encode()).hexdigest()
            if digest in seen:
                duplicates.append({"original": seen[digest], "duplicate": test.get("path")})
            else:
                seen[digest] = test.get("path")
        recommendations = []
        if requirements_text:
            recommendations.append("Review coverage against UI requirements for gaps.")
        if openapi_yaml:
            recommendations.append("Cross-check OpenAPI operations for missing manual tests.")
        test_plan = [test.get("path") for test in manual_tests][:10]

        llm_feedback = None
        try:
            summary_payload = {
                "duplicates": duplicates,
                "recommendations": recommendations,
                "requirements": bool(requirements_text),
                "openapi": bool(openapi_yaml),
            }
            prompt = (
                "As a QA lead, produce a short prioritised optimization note for manual tests. "
                f"Data: {summary_payload}."
            )
            llm_feedback = await self.llm.generate(prompt)
        except Exception:
            llm_feedback = None

        return {
            "duplicates": duplicates,
            "gaps": [],
            "recommendations": recommendations,
            "test_plan": test_plan,
            "llm_feedback": llm_feedback,
        }
