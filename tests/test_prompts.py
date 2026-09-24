from __future__ import annotations

from helpers import BASE, client, mock_transport
from promptjuggler._generated.models.http_call import HttpCall

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


def test_get_prompt_decodes_fields_and_enum_values_newer_than_the_sdk() -> None:
    # The API adds fields and enum values without a major version, so a published client must
    # decode a response carrying ones it doesn't know.
    revision = {
        **REVISION,
        "model": "gpt-9",
        "modelParams": {"reasoningEffort": "ultra"},
        "responseFormat": {"type": "text", "addedLater": 1},
        "tools": [
            {
                "type": "http",
                "name": "lookup",
                "url": "https://example.com",
                "method": "QUERY",
                "paramsSchema": "{}",
                "failFast": False,
            }
        ],
        "addedLater": True,
    }
    with mock_transport(revision):
        prompt = client().get_prompt("greeting", "production")

    assert prompt.model.value == "gpt-9"
    assert prompt.model_params.reasoning_effort == "ultra"
    tool = prompt.tools[0].actual_instance
    assert isinstance(tool, HttpCall)
    assert tool.method == "QUERY"
