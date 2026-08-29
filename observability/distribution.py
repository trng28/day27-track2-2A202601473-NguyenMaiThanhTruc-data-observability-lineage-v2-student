from __future__ import annotations

from typing import Any, Iterable

import numpy as np


def detect_distribution_shift(
    current_values: Iterable[float],
    baseline_values: Iterable[float],
    *,
    ratio_threshold: float = 3.0,
) -> dict[str, Any]:
    """Detect location and shape drift with a dependency-free KS statistic."""
    cur = np.asarray(list(current_values), dtype=float)
    base = np.asarray(list(baseline_values), dtype=float)
    if cur.size == 0 or base.size == 0:
        return {"is_anomaly": False, "score": 0.0, "method": "ks", "reason": "empty_input"}
    cur_mean = float(np.mean(cur))
    base_mean = float(np.mean(base))
    if base_mean == 0:
        score = float("inf") if cur_mean != 0 else 1.0
    else:
        score = max(abs(cur_mean / base_mean), abs(base_mean / cur_mean)) if cur_mean != 0 else float("inf")
    points = np.sort(np.unique(np.concatenate((cur, base))))
    cur_cdf = np.searchsorted(np.sort(cur), points, side="right") / cur.size
    base_cdf = np.searchsorted(np.sort(base), points, side="right") / base.size
    ks = float(np.max(np.abs(cur_cdf - base_cdf)))
    critical = 1.36 * np.sqrt((cur.size + base.size) / (cur.size * base.size))
    cur_std = float(np.std(cur))
    base_std = float(np.std(base))
    if base_std == 0:
        spread_ratio = float("inf") if cur_std != 0 else 1.0
    elif cur_std == 0:
        spread_ratio = float("inf")
    else:
        spread_ratio = max(cur_std / base_std, base_std / cur_std)
    ratio_anomaly = bool(score >= ratio_threshold)
    ks_anomaly = bool(ks > critical) if cur.size >= 4 and base.size >= 4 else False
    spread_anomaly = bool(spread_ratio >= ratio_threshold)
    return {
        "is_anomaly": ratio_anomaly or ks_anomaly or spread_anomaly,
        "score": max(float(score / ratio_threshold), float(ks / critical), float(spread_ratio / ratio_threshold)),
        "method": "ks+location+scale",
        "reason": (f"ks={ks:.4f}, critical={critical:.4f}; baseline_mean={base_mean:.3f}, "
                   f"current_mean={cur_mean:.3f}, mean_ratio={score:.3f}, spread_ratio={spread_ratio:.3f}"),
    }
