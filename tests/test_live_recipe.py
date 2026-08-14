from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("live_tool_eval", ROOT / "scripts/live_tool_eval.py")
assert SPEC is not None and SPEC.loader is not None
live = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(live)


def test_live_recipe_is_pinned_and_disables_thinking() -> None:
    command = live.build_command(
        base_url="https://api.deepseek.com",
        model="deepseek-v4-pro",
        full=False,
    )
    joined = " ".join(command)
    assert live.LOCK["tool_eval_bench"]["commit"] in joined
    assert '{"thinking":{"type":"disabled"}}' in command
    assert all("API_KEY" not in argument for argument in command)


def test_full_recipe_omits_smoke_filter() -> None:
    command = live.build_command(
        base_url="https://api.deepseek.com",
        model="deepseek-v4-flash",
        full=True,
    )
    assert "--scenarios" not in command
