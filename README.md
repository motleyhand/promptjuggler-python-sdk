# PromptJuggler Python SDK

The official Python client for the [PromptJuggler](https://promptjuggler.com) API. Run
prompts and workflows, manage knowledge bases, and verify webhooks — with pydantic-typed
models and flat, synchronous methods.

## Requirements

- Python 3.10+

## Installation

```bash
pip install promptjuggler
```

## Usage

```python
from promptjuggler import PromptJuggler, RunStatus

pj = PromptJuggler("your-api-key")

# Trigger a run (async — returns the run ID)
created = pj.run_prompt("greeting", "production", {"name": "Ada"})

# Poll for the result
run = pj.get_prompt_run(created.id)
if run.status == RunStatus.COMPLETED:
    print(run.output)
```

Errors surface as `ApiError` (with a `status_code`). Verify incoming webhooks with
`verify_webhook_signature()`.

## Documentation

Full guides and the API reference: **https://docs.promptjuggler.com/sdks/python/overview**

## License

MIT
