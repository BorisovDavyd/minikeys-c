from __future__ import annotations
from typing import List, Dict, Any
import re

from app.llm.cloudru_client import CloudRUClient
from app.utils.errors import ValidationError


class AllureValidator:
    REQUIRED_DECORATORS = ["allure.manual", "allure.label", "allure.feature", "allure.story", "allure.suite", "mark.manual"]

    def __init__(self, llm_client: CloudRUClient | None = None) -> None:
        self.llm = llm_client or CloudRUClient()

    async def validate(self, manual_tests: List[Dict[str, str]], ruleset: str = "default") -> Dict[str, Any]:
        issues = []
        passed = True
        for file in manual_tests:
            content = file.get("content", "") if isinstance(file, dict) else getattr(file, "content", "")
            missing = [decor for decor in self.REQUIRED_DECORATORS if decor not in content]
            if missing:
                passed = False
                path = file.get("path") if isinstance(file, dict) else getattr(file, "path", "")
                issues.append({"file": path, "missing": missing})
            if not re.search(r"Arrange: .*Act: .*Assert:", content, re.DOTALL):
                passed = False
                path = file.get("path") if isinstance(file, dict) else getattr(file, "path", "")
                issues.append({"file": path, "issue": "AAA steps not found"})

        # Leverage Cloud.ru Evolution for an additional narrative check/summary
        llm_feedback = None
        try:
            joined = "\n".join(f"{item.get('file', 'unknown')}: {item}" for item in issues) or "No issues"
            prompt = (
                "Provide a brief QA validation note for Allure manual tests. "
                "Comment on decorator completeness and AAA presence based on these findings:\n" + joined
            )
            llm_feedback = await self.llm.generate(prompt)
        except Exception:
            llm_feedback = None

        return {"passed": passed, "failed": not passed, "issues": issues, "llm_feedback": llm_feedback}
