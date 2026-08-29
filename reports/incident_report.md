# Incident Report: Stale Refund Policy in Support Agent

## Severity

P2. Customer support answers may use an outdated refund policy. Revenue processing is not affected.

## Summary

The knowledge-base batch had publish timestamps three hours behind observation time. Content length remained normal, so a shape-only monitor did not alert. The freshness contract detected the violation against the 60-minute threshold and quarantined the batch before activation.

## Detection

Signal: `kb_documents.published_at` freshness failure.

First observed: during the 2026-08-29 game-day validation run.

## Root Cause

The publish stage delivered an old KB snapshot. Evidence supports an upstream publication or synchronization delay, not content truncation or embedding failure.

## Evidence

1. KB freshness contract failed after publish timestamps moved back three hours.
2. Mean text length stayed within its historical range.
3. Orders contract, revenue anomaly and dbt tests remained healthy.
4. Lineage isolates the affected support knowledge path.

## Blast Radius

```text
kb_documents
  -> kb_active_docs
  -> rag_index
  -> support_agent
```

## Mitigation

Quarantine the stale batch, keep the last known good RAG index, notify owner `support-ai` and pause index promotion.

## Recovery

Republish the latest documents, rebuild the active KB and RAG index, then switch traffic after freshness and retrieval smoke checks pass.

## Verification

* [x] Orders contract healthy
* [x] dbt tests healthy
* [x] Revenue anomaly healthy
* [x] KB freshness failure reproduced
* [x] Blast radius identified
* [ ] Fresh production KB received and indexed
* [ ] Support Agent answers verified against current policy

The last two items remain production actions and are not claimed from a synthetic run.

## Prevention and Action Items

| Action | Owner | Deadline | Reason |
|---|---|---|---|
| Enforce freshness before index promotion | support-ai | Next sprint | Prevent stale activation |
| Keep last known good index | platform | Next sprint | Enable safe rollback |
| Add policy retrieval canary | support-ai | Two sprints | Verify user-facing behavior |
| Alert on sustained KB SLO burn | reliability | Two sprints | Avoid transient pages |
