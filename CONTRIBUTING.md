# Contributing

Protocol fixtures should be minimal, sanitized, and tied to one observable boundary. State exact expected finding codes in `cases/manifest.json`; do not add a broad log dump.

Live model results need the original `tool-eval-bench` report plus model, endpoint family, thinking mode, scenario set, seed, tool-eval commit, completion rate, and run date. API keys and private prompts are never acceptable.

Run before opening a pull request:

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run pytest
uv run dsv4-compat-lab run --check
```

Keep protocol findings and model-quality claims separate in prose and filenames.
