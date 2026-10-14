from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "lab.lock.json").read_text(encoding="utf-8"))
SMOKE_SCENARIOS = ["TC-01", "TC-02", "TC-03", "TC-04", "TC-05"]


def build_command(*, base_url: str, model: str, full: bool) -> list[str]:
    dependency = LOCK["tool_eval_bench"]
    command = [
        "uvx",
        "--from",
        f"git+{dependency['repository']}.git@{dependency['commit']}",
        "tool-eval-bench",
        "run",
        "--format",
        "openai",
        "--backend",
        "litellm",
        "--base-url",
        base_url,
        "--model",
        model,
        "--backend-kwargs",
        '{"thinking":{"type":"disabled"}}',
        "--seed",
        "42",
        "--reference-date",
        "2026-08-14",
        "--parallel",
        "1",
        "--output-dir",
        "runs/tool-eval",
        "--label",
        f"deepseek-v4-compat-lab {dependency['commit'][:12]}",
    ]
    if not full:
        command.extend(["--scenarios", *SMOKE_SCENARIOS])
    return command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print or run the pinned non-thinking DeepSeek tool-eval-bench recipe."
    )
    parser.add_argument("--execute", action="store_true", help="make real API calls")
    parser.add_argument("--full", action="store_true", help="run the full standard scenario set")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("DEEPSEEK_BASE_URL", LOCK["deepseek_api"]["base_url"]),
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
    )
    args = parser.parse_args(argv)
    _validate_url(args.base_url)
    command = build_command(base_url=args.base_url, model=args.model, full=args.full)
    print(shlex.join(command))
    print(
        "This recipe disables thinking because the pinned upstream adapter does not yet round-trip "
        "reasoning_content in multi-turn tool histories.",
        file=sys.stderr,
    )
    if not args.execute:
        return 0

    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("TOOL_EVAL_API_KEY")
    if not api_key:
        print("live-tool-eval: set DEEPSEEK_API_KEY before --execute", file=sys.stderr)
        return 2
    child_env = os.environ.copy()
    child_env["TOOL_EVAL_API_KEY"] = api_key
    return subprocess.run(command, env=child_env, check=False).returncode


def _validate_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.username is not None or parsed.password is not None:
        raise ValueError(
            "base URL must not contain credentials; use the API-key environment variable"
        )
    if parsed.scheme == "https" and parsed.netloc:
        return
    if parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        return
    raise ValueError("base URL must use HTTPS, except for an explicit localhost endpoint")


if __name__ == "__main__":
    raise SystemExit(main())
