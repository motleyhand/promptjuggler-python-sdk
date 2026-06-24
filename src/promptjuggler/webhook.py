from __future__ import annotations

import hashlib
import hmac
import time


def verify_webhook_signature(
    payload: str,
    signature_header: str,
    secret: str,
    tolerance: int = 300,
    now: int | None = None,
) -> bool:
    """Verify a PromptJuggler webhook signature.

    PromptJuggler signs each delivery with the ``PromptJuggler-Signature`` header
    (``t=<unix-ts>,v1=<hex-hmac>``); the HMAC-SHA256 is computed over
    ``<timestamp>.<raw-body>``.

    Args:
        payload: The raw request body, exactly as received (verify before JSON parsing).
        signature_header: The ``PromptJuggler-Signature`` header value.
        secret: The webhook signing secret.
        tolerance: Max age, in seconds, of the signature timestamp (replay window).
        now: Current Unix time in seconds. Defaults to the system clock (override for testing).

    Returns:
        Whether ``signature_header`` is a valid signature for ``payload``.
    """
    parsed = _parse_signature_header(signature_header)
    if parsed is None:
        return False

    timestamp, signature = parsed
    current = int(time.time()) if now is None else now
    if abs(current - timestamp) > tolerance:
        return False

    expected = hmac.new(secret.encode(), f"{timestamp}.{payload}".encode(), hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected, signature)


def _parse_signature_header(header: str) -> tuple[int, str] | None:
    fields: dict[str, str] = {}
    for part in header.split(","):
        key, sep, value = part.partition("=")
        if sep and value:
            fields[key.strip()] = value.strip()

    timestamp = fields.get("t")
    signature = fields.get("v1")
    if timestamp is None or signature is None or not timestamp.isdigit():
        return None

    return int(timestamp), signature
