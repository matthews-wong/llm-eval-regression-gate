"""Small paired-comparison statistics with no third-party dependencies."""

import random
from math import comb
from statistics import mean


def mcnemar_exact(regressed: int, fixed: int) -> float:
    """Two-sided exact McNemar p-value from the discordant pair counts.

    Under the null hypothesis a discordant case is equally likely to have
    regressed or been fixed, so the count follows Binomial(n, 0.5). The exact
    form is used because eval sets are small and the chi-square approximation
    is unreliable below roughly 25 discordant pairs.
    """
    if regressed < 0 or fixed < 0:
        raise ValueError(f"counts must be non-negative, got {regressed} and {fixed}")
    n = regressed + fixed
    if n == 0:
        return 1.0
    tail = sum(comb(n, k) for k in range(min(regressed, fixed) + 1)) / 2**n
    return min(1.0, 2 * tail)


def paired_bootstrap_ci(
    deltas: list[float],
    *,
    resamples: int = 2000,
    confidence: float = 0.95,
    seed: int = 0,
) -> tuple[float, float]:
    """Percentile CI for the mean of per-case score deltas.

    Seeded so that the same inputs always give the same verdict in CI.
    """
    if not deltas:
        raise ValueError("cannot bootstrap an empty list of deltas")
    if not 0 < confidence < 1:
        raise ValueError(f"confidence must be in (0, 1), got {confidence}")
    rng = random.Random(seed)
    size = len(deltas)
    means = sorted(mean(rng.choices(deltas, k=size)) for _ in range(resamples))
    alpha = (1 - confidence) / 2
    low = means[int(alpha * resamples)]
    high = means[min(resamples - 1, int((1 - alpha) * resamples))]
    return low, high
