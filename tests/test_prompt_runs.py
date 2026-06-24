from __future__ import annotations

from helpers import BASE, client, mock_transport

RUN_ID = "550e8400-e29b-41d4-a716-446655440000"
THREAD_ID = "550e8400-e29b-41d4-a716-446655440001"
RESPONSE = {"id": RUN_ID, "thread": THREAD_ID}


def test_run_prompt_posts_inputs_only_by_default() -> None:
    with mock_transport(RESPONSE) as calls:
        client().run_prompt("greeting", "production", {"name": "Ada"})

    assert calls[0].method == "POST"
    assert calls[0].url == f"{BASE}/api/v1/prompts/greeting/production/runs"
    assert calls[0].headers["Authorization"] == "Bearer test-key"
    assert calls[0].json()["inputs"] == {"name": "Ada"}


def test_run_prompt_serializes_options_and_array_metadata() -> None:
    with mock_transport(RESPONSE) as calls:
        client().run_prompt(
            "greeting",
            1,
            {"topic": "AI safety"},
            priority="onsite",
            thread=THREAD_ID,
            environment="staging",
            env_vars={"MY_API_KEY": "sk-x"},
            metadata={"tags": ["a", "b"], "user_id": "42"},
            channel="support",
        )

    body = calls[0].json()
    assert body["inputs"] == {"topic": "AI safety"}
    assert body["priority"] == "onsite"
    assert body["environment"] == "staging"
    assert body["envVars"] == {"MY_API_KEY": "sk-x"}
    assert body["metadata"] == {"tags": ["a", "b"], "user_id": "42"}
    assert body["channel"] == "support"


def test_get_prompt_run_gets_by_id() -> None:
    run = {"id": RUN_ID, "status": "completed", "createdAt": "2026-01-01T00:00:00Z", "output": "Hi Ada"}
    with mock_transport(run) as calls:
        client().get_prompt_run(RUN_ID)

    assert calls[0].method == "GET"
    assert calls[0].url == f"{BASE}/api/v1/promptruns/{RUN_ID}"
