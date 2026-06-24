from __future__ import annotations

from helpers import BASE, client, mock_transport

DOC = {
    "id": "550e8400-e29b-41d4-a716-446655440060",
    "status": "pending",
    "fileName": "manual.pdf",
    "bytes": 3,
    "chunkCount": 0,
}


def test_get_knowledge_base_gets_by_slug() -> None:
    kb = {
        "id": "550e8400-e29b-41d4-a716-446655440061",
        "slug": "product-docs",
        "status": "ready",
        "documentCount": 0,
        "chunkCount": 0,
        "documents": [],
    }
    with mock_transport(kb) as calls:
        client().get_knowledge_base("product-docs")

    assert calls[0].method == "GET"
    assert calls[0].url == f"{BASE}/api/v1/knowledge-bases/product-docs"
    assert calls[0].headers["Authorization"] == "Bearer test-key"


def test_upload_documents_sends_bracketed_multipart_with_filenames() -> None:
    with mock_transport([DOC, DOC]) as calls:
        client().upload_documents("product-docs", [("manual.pdf", b"abc"), ("notes.txt", b"hello")])

    assert calls[0].method == "POST"
    assert calls[0].url == f"{BASE}/api/v1/knowledge-bases/product-docs/documents"
    assert [field[0] for field in calls[0].fields] == ["files[0]", "files[1]"]
    assert calls[0].fields[0][1][0] == "manual.pdf"  # (name, (filename, bytes, mime))


def test_upload_documents_returns_created_documents() -> None:
    with mock_transport([DOC, DOC]):
        docs = client().upload_documents("product-docs", [("a.txt", b"x")])

    assert len(docs) == 2
    assert str(docs[0].id) == DOC["id"]
