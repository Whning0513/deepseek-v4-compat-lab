from __future__ import annotations

from deepseek_v4_compat_lab.suite import load_manifest, render_matrix, run_suite


def test_manifest_is_valid_and_unique() -> None:
    manifest = load_manifest()
    identifiers = [case["id"] for case in manifest["cases"]]
    assert len(identifiers) == len(set(identifiers))


def test_all_offline_cases_match() -> None:
    result = run_suite()
    assert result["summary"] == {"cases": 9, "matched": 9, "mismatched": 0}


def test_matrix_labels_results_as_fixtures() -> None:
    output = render_matrix(run_suite())
    assert "conformance fixtures, not model scores" in output
    assert "9/9 fixtures matched" in output
