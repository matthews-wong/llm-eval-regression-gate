"""Load eval results from JSONL into a mapping of case id to result."""

import json
from dataclasses import dataclass
from pathlib import Path


class ResultsError(ValueError):
    """Raised when a results file is malformed."""


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    passed: bool
    score: float


def parse_line(line: str, where: str) -> CaseResult:
    try:
        row = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ResultsError(f"{where}: invalid JSON ({exc.msg})") from exc
    if not isinstance(row, dict):
        raise ResultsError(f"{where}: expected an object, got {type(row).__name__}")
    case_id = row.get("id")
    if not isinstance(case_id, str) or not case_id:
        raise ResultsError(f"{where}: missing string 'id'")
    passed = row.get("passed")
    if not isinstance(passed, bool):
        raise ResultsError(f"{where}: case {case_id!r} needs boolean 'passed'")
    score = row.get("score", 1.0 if passed else 0.0)
    # bool is an int subclass; a True score is almost certainly a typo.
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ResultsError(f"{where}: case {case_id!r} has non-numeric 'score' {score!r}")
    return CaseResult(case_id, passed, float(score))


def load_results(path: Path) -> dict[str, CaseResult]:
    results: dict[str, CaseResult] = {}
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            result = parse_line(line, f"{path}:{number}")
            if result.case_id in results:
                raise ResultsError(f"{path}:{number}: duplicate case id {result.case_id!r}")
            results[result.case_id] = result
    return results
