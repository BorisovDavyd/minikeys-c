import os
import httpx
from typing import Any

from app.utils.logging import logger


class GitLabClient:
    def __init__(self, token: str | None = None, base_url: str | None = None):
        self.token = token or os.getenv("GITLAB_TOKEN")
        self.base_url = base_url or os.getenv("GITLAB_BASE_URL", "https://gitlab.com/api/v4")
        self.mock = not bool(self.token)

    async def fetch_project(self, project_id: str) -> Any:
        if self.mock:
            return {"id": project_id, "mock": True}
        headers = {"PRIVATE-TOKEN": self.token}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/projects/{project_id}", headers=headers)
            response.raise_for_status()
            return response.json()
