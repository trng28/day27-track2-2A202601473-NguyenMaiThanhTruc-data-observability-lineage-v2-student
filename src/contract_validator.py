"""Simple contract validator used as the starter baseline.

The implementation intentionally covers only common deterministic checks.
Students are expected to extend it with:
- stronger type validation/coercion rules,
- freshness checks,
- cross-field/cross-table assertions,
- severity-aware actions (block/quarantine/warn),
- richer observability metadata.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def _issue(
    check: str,
    *,
    column: str | None,
    severity: str,
    passed: bool,
    details: str,
) -> dict[str, Any]:
    action_by_severity = {"critical": "block", "warning": "quarantine", "info": "warn"}
    return {
        "check": check,
        "column": column,
        "severity": severity,
        "passed": bool(passed),
        "details": details,
        "action": "none" if passed else action_by_severity.get(severity, "warn"),
    }


def load_contract(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_dataframe(df: pd.DataFrame, contract: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    columns = contract.get("columns", contract.get("fields", {}))

    for column, rules in columns.items():
        severity = rules.get("severity", "warning")
        required = bool(rules.get("required", False))

        if column not in df.columns:
            if required:
                issues.append(
                    _issue(
                        "required_column",
                        column=column,
                        severity=severity,
                        passed=False,
                        details=f"Missing required column: {column}",
                    )
                )
            continue

        series = df[column]

        declared_type = rules.get("type")
        if declared_type:
            non_null = series.dropna()
            if declared_type == "integer":
                parsed = pd.to_numeric(non_null, errors="coerce")
                valid = parsed.notna() & (parsed % 1 == 0)
            elif declared_type == "number":
                valid = pd.to_numeric(non_null, errors="coerce").notna()
            elif declared_type == "datetime":
                valid = pd.to_datetime(non_null, errors="coerce", utc=True).notna()
            elif declared_type == "boolean":
                valid = non_null.map(lambda value: isinstance(value, bool))
            elif declared_type == "string":
                valid = non_null.map(lambda value: isinstance(value, str))
            else:
                valid = pd.Series(False, index=non_null.index)
            invalid_count = int((~valid).sum())
            issues.append(
                _issue(
                    "type",
                    column=column,
                    severity=severity,
                    passed=(invalid_count == 0),
                    details=f"declared_type={declared_type}; invalid_count={invalid_count}",
                )
            )

        if required:
            null_count = int(series.isna().sum())
            issues.append(
                _issue(
                    "not_null",
                    column=column,
                    severity=severity,
                    passed=(null_count == 0),
                    details=f"null_count={null_count}",
                )
            )

        if rules.get("unique"):
            duplicate_count = int(series.duplicated(keep=False).sum())
            issues.append(
                _issue(
                    "unique",
                    column=column,
                    severity=severity,
                    passed=(duplicate_count == 0),
                    details=f"duplicate_rows={duplicate_count}",
                )
            )

        accepted = rules.get("accepted_values")
        if accepted is not None:
            invalid_mask = series.notna() & ~series.isin(accepted)
            invalid_count = int(invalid_mask.sum())
            issues.append(
                _issue(
                    "accepted_values",
                    column=column,
                    severity=severity,
                    passed=(invalid_count == 0),
                    details=f"invalid_count={invalid_count}; accepted={accepted}",
                )
            )

        if "min_length" in rules:
            lengths = series.dropna().astype(str).str.len()
            invalid_count = int((lengths < int(rules["min_length"])).sum())
            issues.append(
                _issue("min_length", column=column, severity=severity,
                       passed=(invalid_count == 0),
                       details=f"invalid_count={invalid_count}; min_length={rules['min_length']}")
            )

        # Starter numeric range support. Type validation is intentionally minimal.
        if "min" in rules or "max" in rules:
            numeric = pd.to_numeric(series, errors="coerce")
            invalid = series.notna() & numeric.isna()
            if "min" in rules:
                invalid |= numeric < rules["min"]
            if "max" in rules:
                invalid |= numeric > rules["max"]
            invalid_count = int(invalid.fillna(False).sum())
            issues.append(
                _issue(
                    "range",
                    column=column,
                    severity=severity,
                    passed=(invalid_count == 0),
                    details=f"invalid_count={invalid_count}",
                )
            )

    freshness = contract.get("freshness")
    if freshness:
        column = freshness.get("column")
        severity = freshness.get("severity", "warning")
        max_delay = float(freshness.get("max_delay_minutes", 0))
        if column not in df.columns:
            issues.append(_issue("freshness", column=column, severity=severity, passed=False,
                                 details="freshness column is missing"))
        else:
            timestamps = pd.to_datetime(df[column], errors="coerce", utc=True)
            if timestamps.notna().sum() == 0:
                issues.append(_issue("freshness", column=column, severity=severity, passed=False,
                                     details="no valid freshness timestamp"))
            else:
                reference_column = freshness.get("reference_column", "created_at")
                if reference_column in df.columns:
                    reference = pd.to_datetime(df[reference_column], errors="coerce", utc=True).max()
                else:
                    configured = freshness.get("reference_time")
                    reference = (pd.to_datetime(configured, errors="coerce", utc=True)
                                 if configured else pd.Timestamp.now(tz="UTC"))
                latest = timestamps.max()
                delay = max(0.0, float((reference - latest).total_seconds() / 60)) if pd.notna(reference) else 0.0
                issues.append(_issue("freshness", column=column, severity=severity,
                                     passed=(delay <= max_delay),
                                     details=f"delay_minutes={delay:.2f}; max_delay_minutes={max_delay:.2f}"))

    return issues


def failed_issues(issues: list[dict[str, Any]], min_severity: str | None = None) -> list[dict[str, Any]]:
    failed = [i for i in issues if not i.get("passed", False)]
    if min_severity is None:
        return failed
    order = {"info": 0, "warning": 1, "critical": 2}
    threshold = order[min_severity]
    return [i for i in failed if order.get(i.get("severity", "warning"), 1) >= threshold]
