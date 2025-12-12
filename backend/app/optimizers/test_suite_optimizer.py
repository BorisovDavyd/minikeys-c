from __future__ import annotations
from typing import List, Dict, Any
import hashlib


class TestSuiteOptimizer:
    def optimize(self, manual_tests: List[Dict[str, str]], requirements_text: str | None, openapi_yaml: str | None) -> Dict[str, Any]:
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
        return {
            "duplicates": duplicates,
            "gaps": [],
            "recommendations": recommendations,
            "test_plan": test_plan,
        }
