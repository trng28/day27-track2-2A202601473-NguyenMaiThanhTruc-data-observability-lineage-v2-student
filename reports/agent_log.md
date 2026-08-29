# AI Agent Decision Log

## Decision 1: Contract actions

Hypothesis: boolean pass hoặc fail không đủ để pipeline phản ứng đúng.

Proposal: critical thành block, warning thành quarantine và info thành warn.

Evidence: duplicate key tạo critical block; stale KB tạo warning quarantine.

Decision: accept. Kết quả dùng trực tiếp trong orchestration.

## Decision 2: Robust anomaly

Hypothesis: Z-score dễ sai khi có outlier hoặc seasonality.

Proposal: giữ Z-score, dùng MAD cho auto, hỗ trợ same-segment và known-event.

Evidence: healthy score 0.75; volume drop score 13.36; weekend test không alert.

Decision: accept sau khi sửa baseline về cùng độ hạt dữ liệu.

## Decision 3: SCD join

Hypothesis: hai active customer rows làm revenue bị nhân đôi.

Proposal: chọn row mới nhất theo `valid_from` và thêm native unit test.

Evidence: unit test revenue 170 pass; dbt build 16/16.

Decision: accept.

## Decision 4: Multi-window SLO

Hypothesis: short-window burn đơn lẻ tạo false alarm.

Proposal: yêu cầu short và long window cùng vượt ngưỡng.

Evidence: burn 20 và 8 page; burn 20 và 1 không page.

Decision: accept, cần hiệu chỉnh ngưỡng với production traffic.

## Decision 5: KB freshness

Hypothesis: text length không thể phát hiện snapshot cũ nhưng đủ nội dung.

Proposal: validate `published_at` theo thời gian quan sát.

Evidence: stale KB không có length anomaly nhưng có freshness failure.

Decision: accept, quarantine và giữ last known good index.

## Decision 6: Distribution shape

Hypothesis: mean ratio bỏ sót phân phối hai cực cùng trung bình.

Proposal: kết hợp KS, location ratio và scale ratio.

Evidence: robustness test với baseline quanh 10 và current 0/20 pass.

Decision: accept.
