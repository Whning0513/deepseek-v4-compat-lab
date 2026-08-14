from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from dsv4doctor.stream import inspect_stream
from dsv4doctor.validator import validate_request
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "cases" / "manifest.json"
SCHEMA_PATH = ROOT / "cases" / "schema.json"
LOCK_PATH = ROOT / "lab.lock.json"
RESULT_PATH = ROOT / "results" / "offline.json"
MATRIX_PATH = ROOT / "MATRIX.md"


def load_manifest() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    issues = sorted(
        Draft202012Validator(schema).iter_errors(manifest),
        key=lambda item: list(item.path),
    )
    if issues:
        message = "; ".join(f"{list(issue.path)}: {issue.message}" for issue in issues)
        raise ValueError(message)
    identifiers = [case["id"] for case in manifest["cases"]]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("case ids must be unique")
    return manifest


def run_suite() -> dict[str, Any]:
    manifest = load_manifest()
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    results = [_run_case(case) for case in manifest["cases"]]
    return {
        "schema_version": 1,
        "suite": manifest["suite"],
        "protocol_doctor": lock["protocol_doctor"],
        "summary": {
            "cases": len(results),
            "matched": sum(result["matched"] for result in results),
            "mismatched": sum(not result["matched"] for result in results),
        },
        "cases": results,
    }


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    fixture = (ROOT / case["fixture"]).resolve()
    fixture.relative_to((ROOT / "fixtures").resolve())
    if case["kind"] == "request":
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        report = validate_request(payload, source=case["fixture"])
    else:
        with fixture.open("r", encoding="utf-8") as stream:
            report = inspect_stream(stream, source=case["fixture"])

    actual_report = report.to_dict()
    actual = {
        "ok": actual_report["ok"],
        **actual_report["summary"],
        "codes": sorted(item["code"] for item in actual_report["findings"]),
    }
    expected = case["expected"] | {"codes": sorted(case["expected"]["codes"])}
    return {
        "id": case["id"],
        "feature": case["feature"],
        "kind": case["kind"],
        "fixture": case["fixture"],
        "fixture_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
        "matched": actual == expected,
        "expected": expected,
        "actual": actual,
        "findings": actual_report["findings"],
    }


def render_matrix(result: dict[str, Any]) -> str:
    lines = [
        "# Offline Protocol Matrix",
        "",
        (
            "These are conformance fixtures, not model scores. A matched row means the pinned "
            "checker produced the expected diagnostics."
        ),
        "",
        "| Case | Boundary | Expected codes | Result |",
        "| --- | --- | --- | --- |",
    ]
    for case in result["cases"]:
        codes = ", ".join(f"`{code}`" for code in case["actual"]["codes"]) or "none"
        status = "matched" if case["matched"] else "mismatch"
        lines.append(f"| `{case['id']}` | {case['feature']} | {codes} | {status} |")
    summary = result["summary"]
    lines.extend(
        [
            "",
            f"Summary: {summary['matched']}/{summary['cases']} fixtures matched; "
            f"{summary['mismatched']} mismatched.",
            "",
        ]
    )
    return "\n".join(lines)


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
