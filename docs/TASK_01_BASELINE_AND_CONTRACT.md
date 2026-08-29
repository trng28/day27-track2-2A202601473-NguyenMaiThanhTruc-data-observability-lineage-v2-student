# Task 1: Baseline và Data Contract

`orders` cấp dữ liệu cho revenue mart và CEO dashboard. `kb_documents` cấp dữ liệu cho RAG index và Support Agent. Cả hai đều là critical path.

Validator hỗ trợ contract dạng `columns` và `fields`. Mỗi check trả về check, column, severity, passed, details và action. Type validation không coi giá trị parse lỗi là hợp lệ. Freshness của orders so với event time trong batch; freshness của KB so với thời gian chạy.

```powershell
python scripts/reset_lab.py
python gx/validate_orders.py
python scripts/run_baseline.py
```

Baseline khỏe có 0 failure. `duplicate_pk` tạo 1 critical unique failure. `stale_kb` tạo 1 warning freshness và action quarantine. Critical failure chặn publish; warning KB giữ last known good index.

