"""Find cases whose outcome flips across repeated runs of the same candidate."""

from .results import CaseResult, ResultsError


def find_flaky(runs: list[dict[str, CaseResult]]) -> tuple[str, ...]:
    if len(runs) < 2:
        raise ResultsError(f"flaky detection needs at least 2 runs, got {len(runs)}")
    reference = set(runs[0])
    for index, run in enumerate(runs[1:], start=2):
        unmatched = sorted(reference ^ set(run))
        if unmatched:
            raise ResultsError(f"run {index} covers different cases, unmatched ids: {', '.join(unmatched)}")
    return tuple(sorted(i for i in reference if len({run[i].passed for run in runs}) > 1))
