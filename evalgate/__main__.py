"""Command line entry point: python3 -m evalgate baseline.jsonl candidate.jsonl."""

import argparse
import sys
from pathlib import Path

from .compare import Comparison, compare
from .gate import DEFAULT_ALPHA, evaluate
from .results import ResultsError, load_results

EXIT_OK = 0
EXIT_REGRESSION = 1
EXIT_BAD_INPUT = 2


def read_must_pass(path: Path) -> frozenset[str]:
    lines = (line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    return frozenset(line for line in lines if line and not line.startswith("#"))


def format_report(c: Comparison) -> str:
    low, high = c.delta_ci
    lines = [
        f"cases:      {c.total}",
        f"pass rate:  {c.baseline_pass_rate:.3f} -> {c.candidate_pass_rate:.3f}",
        f"score delta: {c.delta_mean:+.3f} (95% CI {low:+.3f} to {high:+.3f})",
        f"McNemar p:  {c.mcnemar_p:.4f}",
        f"regressed:  {', '.join(c.regressed) or '-'}",
        f"fixed:      {', '.join(c.fixed) or '-'}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evalgate", description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--must-pass", type=Path, help="file of case ids that must not regress")
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    parser.add_argument("--seed", type=int, default=0, help="bootstrap seed")
    args = parser.parse_args(argv)

    try:
        baseline = load_results(args.baseline)
        candidate = load_results(args.candidate)
        must_pass = read_must_pass(args.must_pass) if args.must_pass else frozenset()
        unknown = sorted(must_pass - set(baseline))
        if unknown:
            raise ResultsError(f"must-pass ids not in the run: {', '.join(unknown)}")
        comparison = compare(baseline, candidate, seed=args.seed)
    except (ResultsError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_BAD_INPUT

    print(format_report(comparison))
    verdict = evaluate(comparison, must_pass=must_pass, alpha=args.alpha)
    if verdict.passed:
        print("gate: PASS")
        return EXIT_OK
    for reason in verdict.reasons:
        print(f"gate: FAIL - {reason}")
    return EXIT_REGRESSION


if __name__ == "__main__":
    sys.exit(main())
