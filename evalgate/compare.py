"""Pair up two runs by case id and summarise what changed."""

from dataclasses import dataclass

from .results import CaseResult, ResultsError
from .stats import mcnemar_exact, paired_bootstrap_ci


@dataclass(frozen=True)
class Comparison:
    total: int
    regressed: tuple[str, ...]
    fixed: tuple[str, ...]
    baseline_pass_rate: float
    candidate_pass_rate: float
    mcnemar_p: float
    delta_mean: float
    delta_ci: tuple[float, float]


def compare(
    baseline: dict[str, CaseResult],
    candidate: dict[str, CaseResult],
    *,
    seed: int = 0,
) -> Comparison:
    # Comparing different case sets silently would hide dropped cases.
    missing = sorted(set(baseline) ^ set(candidate))
    if missing:
        raise ResultsError(f"runs cover different cases, unmatched ids: {', '.join(missing)}")
    if not baseline:
        raise ResultsError("both runs are empty")

    ids = sorted(baseline)
    regressed = tuple(i for i in ids if baseline[i].passed and not candidate[i].passed)
    fixed = tuple(i for i in ids if not baseline[i].passed and candidate[i].passed)
    deltas = [candidate[i].score - baseline[i].score for i in ids]
    total = len(ids)
    return Comparison(
        total=total,
        regressed=regressed,
        fixed=fixed,
        baseline_pass_rate=sum(baseline[i].passed for i in ids) / total,
        candidate_pass_rate=sum(candidate[i].passed for i in ids) / total,
        mcnemar_p=mcnemar_exact(len(regressed), len(fixed)),
        delta_mean=sum(deltas) / total,
        delta_ci=paired_bootstrap_ci(deltas, seed=seed),
    )
