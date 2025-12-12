import os
from typing import Any, Dict
import httpx

from app.utils.logging import logger


class CloudRUClient:
    """Wrapper around Cloud.ru Evolution Foundation Model API.

    When MOCK_LLM env var is set to a truthy value, deterministic stub responses are
    returned to keep the system working offline.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or os.getenv("CLOUDRU_BASE_URL", "https://api.cloud.ru/llm")
        self.api_key = api_key or os.getenv("CLOUDRU_API_KEY")
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
                    f"{self.base_url}/v1/generate",
                    json={"prompt": prompt},
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("text", "")
            except httpx.HTTPError as exc:
                logger.error("LLM request failed: %s", exc)
                raise

    def _mock_response(self, prompt: str) -> str:
        # Deterministic simple transformation for tests
        summary = prompt.strip().split("\n")[0][:120]
        return f"MOCK_RESPONSE: {summary}"
