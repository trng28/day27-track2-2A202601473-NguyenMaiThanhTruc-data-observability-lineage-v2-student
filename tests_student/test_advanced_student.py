from pathlib import Path
from datetime import datetime, timedelta, timezone

import pandas as pd

from student_api import (
    column_downstream,
    detect_distribution,
    detect_metric,
    multiwindow_burn,
    rag_embedding_shift,
    validate_orders,
)


ROOT = Path(__file__).resolve().parents[1]


def test_type_drift_is_blocked():
    df = pd.read_csv(ROOT / "data" / "baseline" / "orders.csv")
    df["order_id"] = df["order_id"].astype(object)
    df.loc[0, "order_id"] = "not-an-integer"
    failures = [item for item in validate_orders(df, ROOT / "contracts" / "orders_contract.yaml") if not item["passed"]]
    assert any(item["check"] == "type" and item["action"] == "block" for item in failures)


def test_zero_mad_detects_change():
    assert detect_metric(50, [100] * 7, method="mad")["is_anomaly"] is True


def test_same_weekday_prevents_weekend_false_positive():
    context = {"day_of_week": 5, "same_segment_history": [245, 250, 255, 248, 252]}
    assert detect_metric(251, [600, 610, 590, 605, 250, 255], context=context)["is_anomaly"] is False


def test_known_event_is_suppressed():
    assert detect_metric(10, [100] * 7, context={"known_event": "planned migration"})["is_anomaly"] is False


def test_distribution_shape_shift_with_similar_mean():
    baseline = [9, 9, 10, 10, 10, 11, 11, 10]
    current = [0, 0, 0, 0, 20, 20, 20, 20]
    assert detect_distribution(current, baseline)["is_anomaly"] is True


def test_column_lineage_is_transitive():
    graph = {"raw.a": ["stage.a"], "stage.a": ["mart.total"], "mart.total": ["dashboard.kpi"]}
    assert column_downstream(graph, "raw.a") == ["stage.a", "mart.total", "dashboard.kpi"]


def test_multiwindow_pages_sustained_burn_only():
    assert multiwindow_burn(20, 8)["page"] is True
    assert multiwindow_burn(20, 1)["page"] is False


def test_embedding_norm_collapse_is_detected():
    baseline = [0.98, 1.00, 1.02, 0.99, 1.01]
    assert rag_embedding_shift([0.1, 0.11, 0.09], baseline)["is_anomaly"] is True


def test_stale_kb_is_quarantined():
    stale = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    df = pd.DataFrame([{
        "doc_id": "D1", "version": 1, "effective_at": stale,
        "published_at": stale, "source_uri": "policy://refund",
        "content": "Refund policy content long enough for validation.",
    }])
    failures = [item for item in validate_orders(df, ROOT / "contracts" / "kb_contract.yaml") if not item["passed"]]
    assert any(item["check"] == "freshness" and item["action"] == "quarantine" for item in failures)
