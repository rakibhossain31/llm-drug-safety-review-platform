from __future__ import annotations

import random
from collections.abc import Callable


def bootstrap_interval(
    values: list,
    statistic: Callable[[list], float],
    samples: int = 400,
    seed: int = 20260725,
) -> tuple[float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0
    estimate = float(statistic(values))
    rng = random.Random(seed)
    boot = []
    for _ in range(samples):
        resampled = [values[rng.randrange(len(values))] for _ in values]
        boot.append(float(statistic(resampled)))
    boot.sort()
    lower = boot[max(0, int(samples * 0.025) - 1)]
    upper = boot[min(samples - 1, int(samples * 0.975))]
    return round(estimate, 4), round(lower, 4), round(upper, 4)
