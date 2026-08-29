# Execution Evidence

Thời gian thực thi: 2026-08-29, múi giờ Asia/Saigon.

## Automated tests

```text
...................
19 passed in 0.96s
```

Gồm 10 public tests và 9 robustness tests.

## Healthy baseline

```text
orders rows              : 600
contract failed checks   : 0
critical contract fails  : 0
row-count anomaly        : False (auto:mad, score=0.75)
freshness minutes        : 5.1
KB length anomaly        : False
KB contract failed checks: 0
```

## dbt build

```text
Found 3 models, 10 data tests, 2 seeds, 1 unit test
Completed successfully
PASS=16 WARN=0 ERROR=0 SKIP=0 TOTAL=16
```

## Fault evidence

| Fault | Signal quan sát | Kết luận |
|---|---|---|
| duplicate_pk | 603 rows, 1 critical contract failure | Unique check block batch |
| volume_drop | 150/600 rows, MAD score 13.36 | Anomaly bắt completeness issue |
| stale_kb | Length normal, 1 KB freshness failure | Quarantine stale snapshot |

## Validation flow

```text
Equivalent validation result: PASS
Actions: none
```

Great Expectations 1.21.0 không hỗ trợ Python 3.14 trên máy thực thi. Script dùng stable contract validator tương đương. GX native chạy được trên Python 3.10 đến 3.13 theo yêu cầu của lab.

