# Task 3: Anomaly và Distribution Drift

API giữ Z-score cho trường hợp đơn giản. Chế độ `auto` dùng median và MAD để giảm ảnh hưởng của outlier. `same_segment_history` tránh xem pattern cuối tuần là lỗi. Known event có thể được suppress có chủ đích và vẫn ghi reason.

Distribution detector kết hợp KS statistic cho shape, mean ratio cho location và standard deviation ratio cho scale. Thiết kế này bắt được trường hợp mean không đổi nhưng phân phối trở thành hai cực.

```powershell
python scripts/reset_lab.py
python scripts/inject_fault.py volume_drop
python scripts/run_baseline.py
python -m pytest tests_student/test_advanced_student.py -q
```

Healthy batch 600 dòng có anomaly false, score 0.75. Partial ingestion 150/600 dòng có anomaly true, score 13.36. MAD cần ít nhất năm điểm để ổn định. Known event suppression chỉ nên dùng khi event có owner và thời hạn kết thúc.

