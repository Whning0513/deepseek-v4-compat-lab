from __future__ import annotations

import argparse
import sys

from . import __version__
from .suite import MATRIX_PATH, RESULT_PATH, canonical_json, render_matrix, run_suite


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    result = run_suite()
    result_text = canonical_json(result)
    matrix_text = render_matrix(result)
    if args.check:
        if not RESULT_PATH.exists() or RESULT_PATH.read_text(encoding="utf-8") != result_text:
            print("results/offline.json is out of date", file=sys.stderr)
            return 1
        if not MATRIX_PATH.exists() or MATRIX_PATH.read_text(encoding="utf-8") != matrix_text:
            print("MATRIX.md is out of date", file=sys.stderr)
            return 1
    elif args.write:
        RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RESULT_PATH.write_text(result_text, encoding="utf-8")
        MATRIX_PATH.write_text(matrix_text, encoding="utf-8")
    else:
        print(result_text, end="")

    return 1 if result["summary"]["mismatched"] else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dsv4-compat-lab",
        description="Run pinned offline protocol fixtures for DeepSeek V4 clients.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command")
    run = subparsers.add_parser("run", help="run the offline fixture suite")
    mode = run.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="compare with committed outputs")
    mode.add_argument("--write", action="store_true", help="update committed outputs")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
