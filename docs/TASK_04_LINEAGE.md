# Task 4: Lineage và Blast Radius

Traversal dùng BFS, có tập `seen` để chống cycle và trả kết quả ổn định. Logic này áp dụng cho cả dataset và column lineage.

```text
stg_orders
  -> fct_daily_revenue
  -> ceo_revenue_dashboard
```

```text
raw_orders.amount
  -> stg_orders.amount_usd
  -> fct_daily_revenue.daily_revenue
  -> ceo_revenue_dashboard.revenue
```

```powershell
python -m pytest tests_public/test_lineage.py tests_student/test_advanced_student.py -q
```

Sau `dbt build`, `dbt_project/target/manifest.json` chứa `child_map` để tạo graph từ artifact thật.

