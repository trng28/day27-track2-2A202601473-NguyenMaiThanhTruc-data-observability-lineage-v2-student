# Task 5: SLI, SLO và Error Budget

Với target 99.5% và 2 bad checks trên 100 checks:

| Chỉ số | Giá trị |
|---|---:|
| Actual bad rate | 2% |
| Allowed bad rate | 0.5% |
| Burn rate | 4.0 |
| Remaining budget | 0% |
| Breached | true |

Multi-window policy chỉ page khi cả cửa sổ ngắn và dài cùng xác nhận burn. Critical dùng short burn từ 14.4 và long burn từ 6. Warning dùng short burn từ 6 và long burn từ 3. Burn 20 và 8 page critical; burn 20 và 1 không page.

```powershell
python -m pytest tests_public/test_slo.py tests_student/test_advanced_student.py -q
```

Ngưỡng production cần hiệu chỉnh theo độ dài window và tốc độ tiêu thụ budget thực tế.

