from __future__ import annotations
import yaml
from typing import List, Dict, Any


class OpenAPIParser:
    def __init__(self, spec_text: str):
        self.spec = yaml.safe_load(spec_text)

    def list_paths(self) -> List[str]:
        return list(self.spec.get("paths", {}).keys())

    def operations(self) -> List[Dict[str, Any]]:
        paths = self.spec.get("paths", {})
        ops = []
        for path, methods in paths.items():
            for method, detail in methods.items():
                ops.append({
                    "method": method.upper(),
                    "path": path,
                    "summary": detail.get("summary", ""),
                    "operationId": detail.get("operationId", ""),
                    "responses": detail.get("responses", {}),
                })
        return ops

    def security_schemes(self) -> Dict[str, Any]:
        return self.spec.get("components", {}).get("securitySchemes", {})
