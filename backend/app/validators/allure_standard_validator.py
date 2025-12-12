from __future__ import annotations
from typing import List, Dict, Any
import re

from app.utils.errors import ValidationError


class AllureValidator:
    REQUIRED_DECORATORS = ["allure.manual", "allure.label", "allure.feature", "allure.story", "allure.suite", "mark.manual"]

    def validate(self, manual_tests: List[Dict[str, str]], ruleset: str = "default") -> Dict[str, Any]:
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
        return {"passed": passed, "failed": not passed, "issues": issues}
