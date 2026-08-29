#!/usr/bin/env python3
"""Small Great Expectations Core 1.21 example.

This file demonstrates the modern dataframe flow with a few expectations.
Students should extend it into a reusable Expectation Suite / Validation
Definition / Checkpoint and design actions based on severity.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    import great_expectations as gx
except ImportError:
    gx = None

from src.contract_validator import failed_issues, load_contract, validate_dataframe


def main() -> None:
    df = pd.read_csv(ROOT / "data" / "incoming" / "orders.csv")
    if gx is None:
        results = validate_dataframe(df, load_contract(ROOT / "contracts" / "orders_contract.yaml"))
        failed = failed_issues(results)
        for result in results:
            print(f"{result['check']:<24} column={str(result['column']):<12} passed={result['passed']}")
        actions = sorted({result["action"] for result in failed})
        print("\nEquivalent validation result:", "PASS" if not failed else "FAIL")
        print("Actions:", ", ".join(actions) if actions else "none")
        raise SystemExit(1 if any(item["severity"] == "critical" for item in failed) else 0)

    context = gx.get_context()

    # Use unique names so re-running inside an ephemeral context is simple.
    data_source = context.data_sources.add_pandas("orders_pandas")
    asset = data_source.add_dataframe_asset(name="orders_dataframe")
    batch_definition = asset.add_batch_definition_whole_dataframe("whole_orders")
    batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

    expectations = [
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="order_id", severity="critical"
        ),
        gx.expectations.ExpectColumnValuesToBeUnique(
            column="order_id", severity="critical"
        ),
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="amount", min_value=0, severity="critical"
        ),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="currency", value_set=["USD", "VND"], severity="critical"
        ),
    ]

    all_ok = True
    for expectation in expectations:
        result = batch.validate(expectation)
        all_ok = all_ok and bool(result.success)
        print(f"{expectation.__class__.__name__:<40} success={result.success}")

    print("\nStarter GX result:", "PASS" if all_ok else "FAIL")
    print("TODO: package these expectations into a Suite + ValidationDefinition + Checkpoint + Actions.")


if __name__ == "__main__":
    main()
