import asyncio
from app.llm.cloudru_client import CloudRUClient


def test_mock_generation():
    client = CloudRUClient()
    out = asyncio.get_event_loop().run_until_complete(client.generate("hello world"))
    assert out.startswith("MOCK_RESPONSE")
