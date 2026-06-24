from __future__ import annotations

import hashlib
import hmac

from promptjuggler import verify_webhook_signature

SECRET = "whsec_test"
PAYLOAD = '{"event":"promptrun.finished","id":"run1"}'
TIMESTAMP = 1_700_000_000


def header(payload: str, secret: str, timestamp: int) -> str:
    signature = hmac.new(secret.encode(), f"{timestamp}.{payload}".encode(), hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


def test_accepts_a_correctly_signed_payload() -> None:
    assert verify_webhook_signature(PAYLOAD, header(PAYLOAD, SECRET, TIMESTAMP), SECRET, 300, TIMESTAMP)


def test_rejects_a_tampered_payload() -> None:
    signed = header(PAYLOAD, SECRET, TIMESTAMP)
    assert not verify_webhook_signature(f"{PAYLOAD} ", signed, SECRET, 300, TIMESTAMP)


def test_rejects_a_wrong_secret() -> None:
    signed = header(PAYLOAD, SECRET, TIMESTAMP)
    assert not verify_webhook_signature(PAYLOAD, signed, "whsec_wrong", 300, TIMESTAMP)


def test_rejects_a_timestamp_outside_the_tolerance() -> None:
    signed = header(PAYLOAD, SECRET, TIMESTAMP)
    assert not verify_webhook_signature(PAYLOAD, signed, SECRET, 300, TIMESTAMP + 301)


def test_accepts_a_timestamp_at_the_edge_of_the_tolerance() -> None:
    signed = header(PAYLOAD, SECRET, TIMESTAMP)
    assert verify_webhook_signature(PAYLOAD, signed, SECRET, 300, TIMESTAMP + 300)


def test_rejects_a_malformed_header() -> None:
    assert not verify_webhook_signature(PAYLOAD, "not-a-signature", SECRET, 300, TIMESTAMP)
