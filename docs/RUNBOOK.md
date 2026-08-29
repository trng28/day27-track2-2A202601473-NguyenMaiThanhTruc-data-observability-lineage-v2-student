# Runbook thực thi lab

## Chuẩn bị

Lab hỗ trợ Python 3.10 đến 3.13. Trên Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Great Expectations 1.21.0 chưa hỗ trợ Python 3.14. Nên dùng Python 3.13 nếu cần chạy GX native.

## Kiểm tra đầy đủ

```powershell
python scripts/reset_lab.py
python scripts/run_baseline.py
python -m pytest tests_public tests_student -q
python scripts/sync_dbt_seeds.py
dbt build --project-dir dbt_project --profiles-dir dbt_project
python gx/validate_orders.py
```

Trạng thái đạt yêu cầu là baseline 600 orders không có failure, 19 test pass, dbt 16 node pass và validation flow trả về `PASS`.

## Fault scenario

Luôn reset trước mỗi scenario:

```powershell
python scripts/reset_lab.py
python scripts/inject_fault.py duplicate_pk
python scripts/run_baseline.py

python scripts/reset_lab.py
python scripts/inject_fault.py volume_drop
python scripts/run_baseline.py

python scripts/reset_lab.py
python scripts/inject_fault.py stale_kb
python scripts/run_baseline.py
```

Kết quả chi tiết nằm tại `reports/latest_metrics.json`. Sau thử nghiệm, chạy lại `python scripts/reset_lab.py`.

| Severity | Action | Ý nghĩa |
|---|---|---|
| critical | block | Dừng publish dữ liệu lỗi |
| warning | quarantine | Cách ly batch để điều tra |
| info | warn | Ghi nhận và theo dõi |

