from __future__ import annotations
from typing import Dict, Any, Tuple
import textwrap
import yaml

from app.parsers.openapi_parser import OpenAPIParser


class AutoApiGenerator:
    def generate(self, openapi_yaml: str, base_url: str, auth: Dict[str, str]) -> Tuple[list[dict[str, str]], str]:
        parser = OpenAPIParser(openapi_yaml)
        operations = parser.operations()
        header = textwrap.dedent(
            """
            import os
            import pytest
            import httpx


            BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
            AUTH_TOKEN = os.getenv("userPlaneApiToken")
            CLIENT = httpx.Client(base_url=BASE_URL)
            """
        )
        body_parts = []
        for op in operations:
            func_name = op.get("operationId") or f"{op['method'].lower()}_{op['path'].strip('/').replace('/', '_').replace('{', '').replace('}', '')}"
            body_parts.append(
                textwrap.dedent(
                    f"""
                    @pytest.mark.api
                    def test_{func_name}():
                        if not AUTH_TOKEN:
                            pytest.skip("Bearer token missing")
                        headers = {{"Authorization": f"Bearer {{AUTH_TOKEN}}"}}
                        response = CLIENT.request("{op['method']}", "{op['path']}", headers=headers)
                        assert response.status_code < 500
                        assert isinstance(response.json(), (dict, list))
                    """
                )
            )
        content = header + "\n".join(body_parts)
        files = [{"path": "tests/auto_api/test_api_generated.py", "content": content}]
        summary = f"Generated {len(operations)} API tests from OpenAPI"
        return files, summary
