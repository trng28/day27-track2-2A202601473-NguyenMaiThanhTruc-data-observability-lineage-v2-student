# Task 6: RAG Observability

Mean text length phát hiện content collapse. Median embedding norm và MAD phát hiện embedding-space drift từ norm tính sẵn. Freshness contract trên `published_at` bắt snapshot cũ dù content và embedding vẫn có hình dạng bình thường.

```powershell
python scripts/reset_lab.py
python scripts/inject_fault.py stale_kb
python scripts/run_baseline.py
python -m pytest tests_public/test_rag_metrics.py tests_student/test_advanced_student.py -q
```

Fault lùi `published_at` ba giờ không tạo text-length anomaly, nhưng KB contract tạo 1 freshness failure và action quarantine.

