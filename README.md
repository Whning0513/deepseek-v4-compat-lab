# DeepSeek V4 Compatibility Lab

[中文](README.zh-CN.md)

Small, reproducible checks for DeepSeek V4 client integrations. The lab keeps three questions separate:

| Question | Use |
| --- | --- |
| Did the client assemble a valid request or stream? | The offline fixture matrix in this repository |
| Did the model choose and chain tools well? | The pinned `tool-eval-bench` recipe |
| How fast is a serving stack? | `tool-eval-bench bench --perf` |

It does not publish a model score without running a model, and the offline fixtures are not presented as a benchmark.

## Run the offline suite

Python 3.11+ and [uv](https://docs.astral.sh/uv/) are enough:

```bash
uv sync --locked --all-groups
uv run dsv4-compat-lab run --check
```

The committed [matrix](MATRIX.md) currently covers nine small boundaries: thinking and non-thinking tool loops, missing `reasoning_content`, orphan and pending tool results, strict schemas, interleaved streamed calls, truncated arguments, and malformed SSE.

Every fixture has an SHA-256 in [the machine result](results/offline.json). The checker itself is pinned to a commit of [DeepSeek Protocol Doctor](https://github.com/Whning0513/deepseek-protocol-doctor).

## Optional live tool-quality run

The helper prints the exact pinned command and does nothing else:

```bash
uv run python scripts/live_tool_eval.py
```

Add `--execute` only when you intend to make billable API calls and have set `DEEPSEEK_API_KEY`. See [the live-run notes](docs/tool-eval-bench.md) before comparing results. The current recipe explicitly disables thinking because the pinned upstream benchmark does not yet preserve `reasoning_content` in multi-turn history.

## Current DeepSeek assumptions

The lock file records the official docs checked on 2026-08-14:

- the API base URL remains `https://api.deepseek.com`;
- current model names are `deepseek-v4-pro` and `deepseek-v4-flash`;
- the legacy `deepseek-chat` and `deepseek-reasoner` names were retired on 2026-07-24;
- thinking defaults to enabled, and a thinking tool-call turn must round-trip the original `reasoning_content`.

Sources: [V4 release](https://api-docs.deepseek.com/news/news260424), [thinking mode](https://api-docs.deepseek.com/guides/thinking_mode), and [tool calls](https://api-docs.deepseek.com/guides/tool_calls).

## Add a client capture

Keep it small and sanitized. Add one fixture, state the expected stable finding codes in `cases/manifest.json`, and run:

```bash
uv run dsv4-compat-lab run --write
uv run pytest
```

Do not commit prompts, customer data, credentials, or an edited `reasoning_content` value. For live scores, attach the original benchmark report and full run metadata instead of copying only the headline score.

MIT licensed. This is a community project, not an official DeepSeek component.
