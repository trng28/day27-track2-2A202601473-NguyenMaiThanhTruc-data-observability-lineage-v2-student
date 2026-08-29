# Task 7: Incident Response

Quy trình điều tra gồm xác nhận signal, đối chiếu contract và anomaly, dùng lineage xác định consumer, quarantine dữ liệu lỗi, backfill và chạy lại toàn bộ verification.

| Scenario | Contract | Anomaly | Consumer | Hành động |
|---|---|---|---|---|
| duplicate_pk | Critical fail | Có thể không alert | CEO dashboard | Block batch |
| volume_drop | Pass | MAD alert | CEO dashboard | Dừng publish và backfill |
| stale_kb | Freshness warning | Length bình thường | Support Agent | Quarantine KB |

Incident report nằm tại `reports/incident_report.md`. Evidence nằm tại `reports/evidence.md`.
