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
        "provider": "mistral",
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

    assert prompt.provider.value == "mistral"
    assert prompt.model == "gpt-9"
    assert prompt.model_params.reasoning_effort == "ultra"
    tool = prompt.tools[0].actual_instance
    assert isinstance(tool, HttpCall)
    assert tool.method == "QUERY"


def test_dumping_a_revision_shows_one_of_fields_as_their_variant() -> None:
    # The generator wraps every oneOf in a model of its own; pydantic's dump and repr must show the
    # variant, not the wrapper's plumbing.
    response_format = {"type": "json_schema", "name": "reply", "schema": "{}", "strict": True}
    tool = {
        "type": "prompt",
        "versionRef": {"definitionId": "550e8400-e29b-41d4-a716-446655440012", "idOrTag": "production"},
        "name": "summarize",
        "failFast": True,
    }
    with mock_transport({**REVISION, "responseFormat": response_format, "tools": [tool]}):
        prompt = client().get_prompt("greeting", "production")

    dumped = prompt.model_dump(mode="json", by_alias=True, exclude_none=True)

    assert dumped["responseFormat"] == response_format
    assert dumped["tools"] == [tool]
    included = prompt.model_dump(by_alias=True, include={"response_format": {"name"}, "tools": {0: {"type"}}})
    assert included == {
        "responseFormat": {"name": "reply"},
        "tools": [{"type": "prompt"}],
    }
    assert repr(prompt.response_format).startswith("ResponseFormat(actual_instance=JsonSchemaFormat(")
