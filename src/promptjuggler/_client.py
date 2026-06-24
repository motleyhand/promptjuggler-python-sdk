from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, TypeVar, cast
from uuid import UUID

import urllib3.exceptions

from promptjuggler._generated.api.knowledge_bases_api import KnowledgeBasesApi
from promptjuggler._generated.api.prompt_runs_api import PromptRunsApi
from promptjuggler._generated.api.prompts_api import PromptsApi
from promptjuggler._generated.api.workflow_runs_api import WorkflowRunsApi
from promptjuggler._generated.api_client import ApiClient
from promptjuggler._generated.configuration import Configuration
from promptjuggler._generated.exceptions import ApiException
from promptjuggler._generated.models.create_prompt_run import CreatePromptRun
from promptjuggler._generated.models.create_prompt_run_response import CreatePromptRunResponse
from promptjuggler._generated.models.create_workflow_run import CreateWorkflowRun
from promptjuggler._generated.models.create_workflow_run_metadata_value import CreateWorkflowRunMetadataValue
from promptjuggler._generated.models.create_workflow_run_response import CreateWorkflowRunResponse
from promptjuggler._generated.models.knowledge_base_response import KnowledgeBaseResponse
from promptjuggler._generated.models.knowledge_document_response import KnowledgeDocumentResponse
from promptjuggler._generated.models.prompt_revision import PromptRevision
from promptjuggler._generated.models.prompt_run import PromptRun
from promptjuggler._generated.models.workflow_run import WorkflowRun
from promptjuggler.errors import ApiError, NetworkError

DEFAULT_BASE_URL = "https://promptjuggler.com"

T = TypeVar("T")

# Metadata values are strings or lists of strings; the generated model wraps them in a
# oneOf type, so the facade hides that wrapping.
Metadata = dict[str, "str | list[str]"]


class PromptJuggler:
    """Ergonomic entry point to the PromptJuggler API. Wraps the generated client: flat
    method calls in, generated typed (pydantic) models out, with API errors translated
    into :class:`~promptjuggler.errors.ApiError`.
    """

    def __init__(self, api_key: str, *, base_url: str | None = None) -> None:
        config = Configuration(host=base_url or DEFAULT_BASE_URL, access_token=api_key)
        client = ApiClient(config)
        self._prompts = PromptsApi(client)
        self._prompt_runs = PromptRunsApi(client)
        self._workflow_runs = WorkflowRunsApi(client)
        self._knowledge_bases = KnowledgeBasesApi(client)

    def get_prompt(self, slug: str, version: int | str) -> PromptRevision:
        """Fetch a prompt revision by slug and version (a revision number or a tag like ``production``)."""
        return self._send(lambda: self._prompts.get_prompt_revision(slug, str(version)))

    def run_prompt(
        self,
        slug: str,
        version: int | str,
        inputs: dict[str, str],
        *,
        priority: str | None = None,
        thread: str | UUID | None = None,
        environment: str | None = None,
        env_vars: dict[str, str] | None = None,
        metadata: Metadata | None = None,
        channel: str | None = None,
    ) -> CreatePromptRunResponse:
        """Trigger a prompt run (async — returns the run ID; poll :meth:`get_prompt_run` for the result)."""
        body = CreatePromptRun(
            inputs=inputs,
            priority=priority,
            thread=_uuid(thread) if thread is not None else None,
            environment=environment,
            envVars=env_vars,
            metadata=_wrap_metadata(metadata),
            channel=channel,
        )
        return self._send(lambda: self._prompt_runs.create_prompt_run(slug, str(version), body))

    def get_prompt_run(self, run_id: str | UUID) -> PromptRun:
        """Fetch a prompt run by ID."""
        return self._send(lambda: self._prompt_runs.get_prompt_run(_uuid(run_id)))

    def run_workflow(
        self,
        slug: str,
        version: int | str,
        inputs: dict[str, str],
        *,
        priority: str | None = None,
        thread: str | UUID | None = None,
        environment: str | None = None,
        env_vars: dict[str, str] | None = None,
        metadata: Metadata | None = None,
    ) -> CreateWorkflowRunResponse:
        """Trigger a workflow run (async — returns the run ID; poll :meth:`get_workflow_run`)."""
        body = CreateWorkflowRun(
            inputs=inputs,
            priority=priority,
            thread=_uuid(thread) if thread is not None else None,
            environment=environment,
            envVars=env_vars,
            metadata=_wrap_metadata(metadata),
        )
        return self._send(lambda: self._workflow_runs.create_workflow_run(slug, str(version), body))

    def get_workflow_run(self, run_id: str | UUID) -> WorkflowRun:
        """Fetch a workflow run by ID."""
        return self._send(lambda: self._workflow_runs.get_workflow_run(_uuid(run_id)))

    def get_knowledge_base(self, slug: str) -> KnowledgeBaseResponse:
        """Fetch a knowledge base by slug."""
        return self._send(lambda: self._knowledge_bases.public_get_knowledge_base(slug))

    def get_knowledge_document(self, document_id: str | UUID) -> KnowledgeDocumentResponse:
        """Fetch a knowledge document by ID."""
        return self._send(lambda: self._knowledge_bases.public_get_document(_uuid(document_id)))

    def delete_knowledge_document(self, document_id: str | UUID) -> None:
        """Delete a knowledge document by ID."""
        self._send(lambda: self._knowledge_bases.public_delete_document(_uuid(document_id)))

    def upload_documents(self, slug: str, files: list[tuple[str, bytes]]) -> list[KnowledgeDocumentResponse]:
        """Upload one or more documents to a knowledge base (processed asynchronously).

        Each file is a ``(filename, contents)`` tuple.
        """
        api = self._knowledge_bases
        # The generated serializer names every multipart part "files"; the server needs
        # them bracket-indexed (files[0], files[1], ...) to parse them as an array. Reuse
        # the serializer (it builds the URL, auth, and (filename, bytes, mime) parts),
        # rename the fields, and call through — the Python analogue of an init override.
        method, url, headers, body, post_params = api._public_upload_documents_serialize(
            slug=slug,
            files=list(files),
            _request_auth=None,
            _content_type=None,
            _headers=None,
            _host_index=0,
        )
        bracketed = _bracket_file_fields(cast("list[tuple[str, Any]]", post_params))

        def call() -> list[KnowledgeDocumentResponse]:
            response = api.api_client.call_api(method, url, headers, body, bracketed)
            response.read()
            result = api.api_client.response_deserialize(
                response, {"200": "List[KnowledgeDocumentResponse]", "403": "ErrorResponse"}
            ).data
            return cast("list[KnowledgeDocumentResponse]", result)

        return self._send(call)

    def _send(self, call: Callable[[], T]) -> T:
        try:
            return call()
        except ApiException as error:
            raise _to_api_error(error) from error
        except urllib3.exceptions.HTTPError as error:
            # No response: DNS failure, timeout, refused connection, etc.
            raise NetworkError(str(error)) from error


def _uuid(value: str | UUID) -> UUID:
    return value if isinstance(value, UUID) else UUID(value)


def _bracket_file_fields(post_params: list[tuple[str, Any]]) -> list[tuple[str, Any]]:
    bracketed: list[tuple[str, Any]] = []
    index = 0
    for name, value in post_params:
        if name == "files":
            bracketed.append((f"files[{index}]", value))
            index += 1
        else:
            bracketed.append((name, value))
    return bracketed


def _wrap_metadata(metadata: Metadata | None) -> dict[str, CreateWorkflowRunMetadataValue] | None:
    if metadata is None:
        return None
    return {key: CreateWorkflowRunMetadataValue(value) for key, value in metadata.items()}


def _to_api_error(error: ApiException) -> ApiError:
    message = error.reason or "API request failed"
    body = error.body
    if isinstance(body, (str, bytes)):
        try:
            decoded = json.loads(body)
        except (ValueError, TypeError):
            decoded = None
        if isinstance(decoded, dict) and isinstance(decoded.get("error"), str):
            message = decoded["error"]
    return ApiError(message, error.status)
