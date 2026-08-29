# Task 2: Bảo vệ transformation bằng dbt

Nếu customer có nhiều active version, join có thể nhân mỗi order và làm tăng revenue. Model hiện chọn một active row mới nhất theo `valid_from` trước khi join.

Generic tests kiểm tra not null, unique và accepted values. Singular test bảo vệ doanh thu không âm. Native unit test tạo hai active versions và xác nhận hai orders chỉ tạo revenue 170.

`not_null` và `unique` là data tests vì kiểm tra dữ liệu sau khi model chạy. Unit test cấp fixture nhỏ và so sánh output của logic transformation, nên tái hiện được lỗi join mà không phụ thuộc production data.

```powershell
python scripts/reset_lab.py
python scripts/sync_dbt_seeds.py
dbt build --project-dir dbt_project --profiles-dir dbt_project
```

Evidence: dbt tìm thấy 3 models, 10 data tests, 2 seeds và 1 unit test. Kết quả `PASS=16`, `ERROR=0`, `SKIP=0`.

