from __future__ import annotations

from helpers import BASE, client, mock_transport

RUN_ID = "550e8400-e29b-41d4-a716-446655440020"
THREAD_ID = "550e8400-e29b-41d4-a716-446655440021"
RESPONSE = {"id": RUN_ID, "thread": THREAD_ID}


def test_run_workflow_posts_to_workflow_runs() -> None:
    with mock_transport(RESPONSE) as calls:
        client().run_workflow("onboarding", "production", {"email": "a@b.com"}, metadata={"tags": ["x"]})

    assert calls[0].method == "POST"
    assert calls[0].url == f"{BASE}/api/v1/workflows/onboarding/production/runs"
    body = calls[0].json()
    assert body["inputs"] == {"email": "a@b.com"}
    assert body["metadata"] == {"tags": ["x"]}


def test_get_workflow_run_gets_by_id() -> None:
    run = {
        "id": RUN_ID,
        "status": "completed",
        "createdAt": "2026-01-01T00:00:00Z",
        "outputs": {},
        "errors": [],
    }
    with mock_transport(run) as calls:
        client().get_workflow_run(RUN_ID)

    assert calls[0].method == "GET"
    assert calls[0].url == f"{BASE}/api/v1/workflowruns/{RUN_ID}"
