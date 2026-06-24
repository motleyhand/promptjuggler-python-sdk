from __future__ import annotations

from helpers import BASE, client, mock_transport

DOC_ID = "550e8400-e29b-41d4-a716-446655440030"


def test_get_knowledge_document_gets_by_id() -> None:
    doc = {"id": DOC_ID, "status": "ready", "fileName": "manual.pdf", "bytes": 1234, "chunkCount": 5}
    with mock_transport(doc) as calls:
        client().get_knowledge_document(DOC_ID)

    assert calls[0].method == "GET"
    assert calls[0].url == f"{BASE}/api/v1/knowledge-documents/{DOC_ID}"


def test_delete_knowledge_document_deletes_by_id() -> None:
    with mock_transport(None, status=204) as calls:
        client().delete_knowledge_document(DOC_ID)

    assert calls[0].method == "DELETE"
    assert calls[0].url == f"{BASE}/api/v1/knowledge-documents/{DOC_ID}"
    assert calls[0].headers["Authorization"] == "Bearer test-key"
