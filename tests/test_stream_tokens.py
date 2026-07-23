from __future__ import annotations

from helpers import BASE, client, mock_transport

THREAD = "0198f0e2-9c3a-7c1d-8f4b-2a6d5e7c9b10"
STREAM_URL = f"https://stream.promptjuggler.com/stream/{THREAD}"


def test_create_stream_token_posts_to_thread() -> None:
    body = {"token": "jwt-value", "expiresAt": "2026-01-01T00:00:00+00:00", "url": STREAM_URL}
    with mock_transport(body) as calls:
        client().create_stream_token(THREAD)

    assert calls[0].method == "POST"
    assert calls[0].url == f"{BASE}/api/v1/threads/{THREAD}/stream-token"
    assert calls[0].headers["Authorization"] == "Bearer test-key"


def test_create_stream_token_returns_token_and_resolved_url() -> None:
    body = {"token": "jwt-value", "expiresAt": "2026-01-01T00:00:00+00:00", "url": STREAM_URL}
    with mock_transport(body):
        result = client().create_stream_token(THREAD)

    assert result.token == "jwt-value"
    assert result.url == STREAM_URL
