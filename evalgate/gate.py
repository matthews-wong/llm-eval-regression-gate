"""Turn a comparison into a pass/fail verdict with human-readable reasons."""

from dataclasses import dataclass

from .compare import Comparison

DEFAULT_ALPHA = 0.05


@dataclass(frozen=True)
class Verdict:
    passed: bool
    reasons: tuple[str, ...]


def evaluate(
    comparison: Comparison,
    *,
    must_pass: frozenset[str] = frozenset(),
    alpha: float = DEFAULT_ALPHA,
) -> Verdict:
    reasons: list[str] = []

    pinned = sorted(must_pass.intersection(comparison.regressed))
    if pinned:
        reasons.append(f"must-pass cases regressed: {', '.join(pinned)}")

    significant = comparison.mcnemar_p < alpha
    if significant and len(comparison.regressed) > len(comparison.fixed):
        reasons.append(
            f"significant regression: {len(comparison.regressed)} regressed vs "
            f"{len(comparison.fixed)} fixed (McNemar p={comparison.mcnemar_p:.4f} < {alpha})"
        )
    return Verdict(passed=not reasons, reasons=tuple(reasons))
