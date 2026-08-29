from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from observability.anomaly import zscore_detector


def approximate_token_lengths(texts: Iterable[str]) -> list[int]:
    # Deliberately simple proxy; no tokenizer/model download needed.
    return [len(str(t).split()) for t in texts]


def detect_text_length_shift(
    current_texts: Iterable[str],
    baseline_batch_means: Iterable[float],
    *,
    threshold: float = 3.0,
) -> dict[str, Any]:
    lengths = approximate_token_lengths(current_texts)
    current_mean = float(np.mean(lengths)) if lengths else 0.0
    result = zscore_detector(current_mean, baseline_batch_means, threshold=threshold)
    result["metric"] = "mean_text_length"
    result["current_mean"] = current_mean
    return result


def detect_embedding_norm_shift(
    current_norms: Iterable[float], baseline_norms: Iterable[float]
) -> dict[str, Any]:
    """Detect a robust shift in the mean norm of a current embedding batch."""
    current = np.asarray(list(current_norms), dtype=float)
    baseline = np.asarray(list(baseline_norms), dtype=float)
    if current.size == 0 or baseline.size < 3:
        return {"is_anomaly": False, "score": 0.0, "method": "robust_norm_shift",
                "reason": "insufficient_data"}
    center = float(np.median(baseline))
    mad = float(np.median(np.abs(baseline - center)))
    current_center = float(np.median(current))
    deviation = abs(current_center - center)
    score = 0.0 if deviation == 0 else (float("inf") if mad == 0 else 0.6745 * deviation / mad)
    return {"is_anomaly": bool(score > 3.5), "score": float(score), "method": "robust_norm_shift",
            "reason": f"baseline_median={center:.4f}, current_median={current_center:.4f}, mad={mad:.4f}"}
