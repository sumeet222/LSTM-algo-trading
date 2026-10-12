# Source remediation result

PARTIAL_REMEDIATION — HUMAN_REVIEW_REQUIRED.

Acquired 17,550 genuine pre-July native rows, including every 8,680 expected RTH half-hour from December18 2019 through June30 2020. All65 July1 overlap controls match original OHLCV. Current candidate warmup is content-hashed and stored separately; original data/source defaults remain untouched.

Exactly264 startup rejects recover: train919→1183/1502 (61.19→78.76%). All319 later rejections remain from the original168 gaps. The90% guard needs169 more eligible origins. Alpaca native30Min and15 tight minute retries produced none of the missing keys. A local Massive key became available later; one historical probe returned403 and that branch stopped without access changes.

Data attempts72/180 Alpaca and1/80 Massive.340 tests pass;59 Python files havezero basic Pyright errors/warnings;Ruff and preservation pass. Scientific/source clocks, actions, actual certificates and formal approvals remain HOLD;0/40 neural pairs. No models, performance, confirmation outcomes, source activation or Git integration.

Start with [the six-item review card](human_review_card.md), then [before/after retention](retention_before_after.md) and [gap/access reconciliation](gap_cluster_reconciliation.md). Current metadata is source_acquisition_summary_v2.json and source_extension_manifest_v2.json; earlier primary-only snapshots are preserved with explicit follow-up status.
