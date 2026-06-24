from __future__ import annotations

from helpers import BASE, client, mock_transport

REVISION = {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "promptId": "550e8400-e29b-41d4-a716-446655440011",
    "memory": "stateless",
    "provider": "openai",
    "model": "gpt-4o",
    "modelParams": {},
    "responseFormat": {"type": "text"},
    "messages": [],
    "tools": [],
}


def test_get_prompt_sends_get_with_bearer() -> None:
    with mock_transport(REVISION) as calls:
        client().get_prompt("greeting", "production")

    assert calls[0].method == "GET"
    assert calls[0].url == f"{BASE}/api/v1/prompts/greeting/production"
    assert calls[0].headers["Authorization"] == "Bearer test-key"


def test_get_prompt_accepts_int_version() -> None:
    with mock_transport(REVISION) as calls:
        client().get_prompt("greeting", 42)

    assert calls[0].url == f"{BASE}/api/v1/prompts/greeting/42"
