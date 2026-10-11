# P2.2A review — APPROVE / CORRECT / HOLD

1. `src/lstm_data/labels.py:26` MinuteReference and `:70` exact lookup; `tests/test_labels.py:160` rejects duplicate keys and a10:34/other-symbol replacement for10:33. Nonpositive/nonfinite, non-minute, adjusted or non-open fields reject. Row/version IDs persist; no acquired sources inspected.
2. `src/lstm_data/labels.py:262` label_sample; `tests/test_labels.py:81` recomputes five logs, median0, unscaled MAD0.01; fitted epsilon0.001 and denominator0.011. `target_trace_examples.md` gives all five fake raw opens and scores. Zero-MAD test fits floor0.0001; no clipping or partial population.
3. `src/lstm_data/labels.py:132` causal_eligibility; `tests/test_labels.py:137` future exit removal/publication delay leaves forecast and all entry flags identical. Only future label/maturity changes. Missing contemporaneous entry blocks that name. P3 admission and execution outcome NOT_EVALUATED.
4. `src/lstm_data/labels.py:356` fitting_window and `:382` fitting_membership; `tests/test_labels.py:218` WF1 inner tail starts2023-03-31; boundary crossings purge, validation outliers cannot fit the training floor. Frozen WF1/WF2/preconfirmation stops and actual fitted_at are separate. No confirmation outcomes used.
5. `tests/test_labels.py:192` unknown publication→MATURITY_UNVERIFIED/no fitted population; `:277` explicit4-for-1 split raw100→25 yields zero return, unknown/unsupported actions block. No dividend cashflows or assumed source clock activated.
6. `checks.json`: tested implementation versus overall G2 BLOCKED. Prior P2.1 `signoff_pending.md` remains REPORTED AGREEMENT / FORMAL REGISTRATION PENDING. Full minute coverage,168 historical half-hour gaps, four cash-date records and market HOLD persist; no blocker cleared.

**APPROVE / CORRECT / HOLD** this synthetic interface package. Any source-coverage/availability bridge or P2.2B integration requires a separate prompt; P2.3 is not started.
