from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import patch

import urllib3

from promptjuggler import PromptJuggler

BASE = "https://promptjuggler.com"


class Capture:
    """A single request the SDK put on the wire."""

    def __init__(self, method: str, url: str, body: Any, headers: dict[str, str], fields: Any) -> None:
        self.method = method
        self.url = url
        self.body = body
        self.headers = headers
        self.fields = fields  # multipart form fields (used by uploads)

    def json(self) -> Any:
        return json.loads(self.body)


class _FakeResponse:
    """A read urllib3-style response — only what RESTResponse / ApiClient touch.

    Built directly (rather than urllib3.HTTPResponse) because urllib3 reports an empty
    body's ``.data`` as ``None``, while a real 204 yields ``b""`` — which the generated
    client asserts is non-None.
    """

    def __init__(self, data: bytes, status: int) -> None:
        self.status = status
        self.reason = ""
        self.data = data
        self.headers = urllib3.HTTPHeaderDict({"Content-Type": "application/json"})

    def read(self) -> bytes:
        return self.data


@contextmanager
def mock_transport(data: Any = None, status: int = 200) -> Iterator[list[Capture]]:
    """Patch the urllib3 layer so requests are captured and answered with ``data``.

    Yields the list of captured requests so a test can assert the exact method, URL,
    headers, and body the SDK sent.
    """
    calls: list[Capture] = []

    def fake_request(
        self: urllib3.PoolManager,
        method: str,
        url: str,
        body: Any = None,
        headers: Any = None,
        **kwargs: Any,
    ) -> _FakeResponse:
        calls.append(Capture(method, url, body, dict(headers or {}), kwargs.get("fields")))
        payload = b"" if data is None else json.dumps(data).encode()
        return _FakeResponse(payload, status)

    with patch.object(urllib3.PoolManager, "request", fake_request):
        yield calls


@contextmanager
def mock_network_failure() -> Iterator[None]:
    """Patch the urllib3 layer to raise a connection-level error (no response)."""

    def boom(self: urllib3.PoolManager, method: str, url: str, **kwargs: Any) -> urllib3.HTTPResponse:
        raise urllib3.exceptions.HTTPError("connection refused")

    with patch.object(urllib3.PoolManager, "request", boom):
        yield


def client() -> PromptJuggler:
    return PromptJuggler("test-key")
