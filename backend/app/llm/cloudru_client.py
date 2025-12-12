import os
from typing import Any, Dict
import httpx

from app.utils.logging import logger


class CloudRUClient:
    """Wrapper around Cloud.ru Foundation Models (OpenAI-compatible) API.

    When MOCK_LLM env var is set to a truthy value, deterministic stub responses are
    returned to keep the system working offline.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None, model: str | None = None):
        # Foundation Models OpenAI-compatible endpoint
        self.base_url = base_url or os.getenv(
            "CLOUDRU_BASE_URL", "https://foundation-models.api.cloud.ru"
        )
        self.api_key = api_key or os.getenv("CLOUDRU_API_KEY")
        self.model = model or os.getenv("CLOUDRU_MODEL", "gpt-4o-mini")
        self.mock = bool(os.getenv("MOCK_LLM", "1")) if api_key is None else False

    async def generate(self, prompt: str) -> str:
        if self.mock:
            logger.info("CloudRUClient running in mock mode")
            return self._mock_response(prompt)
        if not self.api_key:
            raise RuntimeError("CLOUDRU_API_KEY is required when not in mock mode")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0,
                    },
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    return ""
                return choices[0].get("message", {}).get("content", "")
            except httpx.HTTPError as exc:
                logger.error("LLM request failed: %s", exc)
                raise

    def _mock_response(self, prompt: str) -> str:
        # Deterministic simple transformation for tests
        summary = prompt.strip().split("\n")[0][:120]
        return f"MOCK_RESPONSE: {summary}"
