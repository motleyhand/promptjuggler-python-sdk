from __future__ import annotations

import pytest

from helpers import client, mock_network_failure, mock_transport
from promptjuggler import ApiError, DecodeError, NetworkError, PromptJugglerError

RUN_ID = "550e8400-e29b-41d4-a716-446655440040"


def test_translates_non_2xx_into_api_error() -> None:
    with mock_transport({"error": "Prompt run not found"}, status=404), pytest.raises(ApiError) as exc_info:
        client().get_prompt_run(RUN_ID)

    assert exc_info.value.status_code == 404
    assert str(exc_info.value) == "Prompt run not found"


def test_api_error_is_a_promptjuggler_error() -> None:
    with mock_transport({"error": "boom"}, status=500), pytest.raises(PromptJugglerError):
        client().get_prompt_run(RUN_ID)


def test_wraps_undecodable_success_body_in_decode_error() -> None:
    revision = {
        "id": RUN_ID,
        "promptId": RUN_ID,
        "memory": "stateless",
        "provider": "openai",
        "model": "gpt-4o",
        "modelParams": {},
        "responseFormat": {"type": "text"},
        "messages": [],
        "tools": "not-a-list",
    }
    with mock_transport(revision), pytest.raises(DecodeError):
        client().get_prompt("greeting", "production")


def test_wraps_network_failure_in_network_error() -> None:
    with mock_network_failure(), pytest.raises(NetworkError) as exc_info:
        client().get_prompt_run(RUN_ID)

    assert isinstance(exc_info.value, PromptJugglerError)
