"""Anomaly detection starter.

Z-score is deliberately the default baseline. Students should improve `auto`
mode for seasonality/outliers rather than deleting the simple implementation.
"""
from __future__ import annotations

from typing import Any, Iterable

import numpy as np


def zscore_detector(current: float, history: Iterable[float], threshold: float = 3.0) -> dict[str, Any]:
    values = np.asarray(list(history), dtype=float)
    if values.size < 3:
        return {"is_anomaly": False, "score": 0.0, "method": "zscore", "reason": "insufficient_history"}
    mean = float(np.mean(values))
    std = float(np.std(values))
    if std == 0:
        score = float("inf") if float(current) != mean else 0.0
    else:
        score = abs(float(current) - mean) / std
    return {
        "is_anomaly": bool(score > threshold),
        "score": float(score),
        "method": "zscore",
        "reason": f"mean={mean:.3f}, std={std:.3f}, threshold={threshold}",
    }


def mad_detector(current: float, history: Iterable[float], threshold: float = 3.5) -> dict[str, Any]:
    """Robust example, intentionally incomplete around zero-MAD edge cases.

    Students may improve this function and/or use it from auto mode.
    """
    values = np.asarray(list(history), dtype=float)
    if values.size < 5:
        return {"is_anomaly": False, "score": 0.0, "method": "mad", "reason": "insufficient_history"}
    median = float(np.median(values))
    mad = float(np.median(np.abs(values - median)))
    if mad == 0:
        deviation = abs(float(current) - median)
        score = float("inf") if deviation > 0 else 0.0
        return {"is_anomaly": bool(deviation > 0), "score": score, "method": "mad",
                "reason": f"median={median:.3f}, mad=0; exact_baseline_comparison"}
    modified_z = 0.6745 * abs(float(current) - median) / mad
    return {
        "is_anomaly": bool(modified_z > threshold),
        "score": float(modified_z),
        "method": "mad",
        "reason": f"median={median:.3f}, mad={mad:.3f}, threshold={threshold}",
    }


def detect_anomaly(
    current: float,
    history: Iterable[float],
    *,
    method: str = "auto",
    threshold: float = 3.0,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Stable lab API.

    Supported behavior:
    - `zscore`: basic z-score.
    - `mad`: robust median absolute deviation detector.
    - `auto`: context-aware MAD with a z-score fallback for short histories.

    Context may include `same_segment_history`, `metric_name`, `known_event`
    and other caller metadata.
    """
    values = list(history)
    if method == "mad":
        return mad_detector(current, values)
    if method == "zscore":
        return zscore_detector(current, values, threshold=threshold)
    if method == "auto":
        context = context or {}
        if context.get("known_event"):
            return {"is_anomaly": False, "score": 0.0, "method": "auto:known_event",
                    "reason": f"suppressed_known_event={context['known_event']}"}
        segment = context.get("same_segment_history")
        selected = list(segment) if segment is not None and len(segment) >= 5 else values
        result = mad_detector(current, selected)
        result["method"] = "auto:same_segment_mad" if selected is not values else "auto:mad"
        if result["reason"] == "insufficient_history":
            result = zscore_detector(current, selected, threshold=threshold)
            result["method"] = "auto:zscore"
        return result
    raise ValueError(f"Unsupported method: {method}")
