# Live tool-quality runs

The offline matrix in this repository checks request and stream shape. It cannot tell whether a model chose the right tool or arguments.

For that job, the lab pins [`tool-eval-bench`](https://github.com/SeraphimSerapis/tool-eval-bench) instead of maintaining another scenario set. The helper prints a five-scenario command by default:

```bash
uv run python scripts/live_tool_eval.py
```

Nothing is sent until `--execute` is added and `DEEPSEEK_API_KEY` is present:

```bash
export DEEPSEEK_API_KEY=...
uv run python scripts/live_tool_eval.py --execute
```

Use `--full` for the standard suite. Runs go to `runs/tool-eval/`, which is ignored by Git.

## Current thinking-mode boundary

At pinned commit `50cf20eb831c2024fcd4cf80227ef1ba37db7c60`, the OpenAI-compatible adapter parses `reasoning_content`, but the orchestrator's next assistant history message does not include it. DeepSeek V4 requires that field to be passed back after a thinking-mode tool call, so a multi-turn run can receive a 400.

The provided live recipe therefore sends `{"thinking":{"type":"disabled"}}`. Do not compare that run with a thinking-enabled run as if they were the same configuration. Thinking mode should be enabled here only after the upstream round-trip path is fixed and pinned.

When publishing a result, include the tool-eval commit, model, endpoint family, thinking mode, scenario set, seed, completion rate, and raw report. Never commit an API key.
