# Final targeted diagnostic handoff

**Completed 6/6 prespecified treatment accounts and 7/7 unchanged controls:**
13 independent $100k continuous 2021–2024 books, one shared 48-month funded pass.
All 7 controls reproduce all 1,005 archived days and terminal totals. M01 is an
explicit identity arm because its original rule already has two confirmations.

| Mechanism | Control → treatment net USD | Interpretation |
|---|---:|---|
| M04 event confirmation | -2,117.97 → -3,615.01 | Falsified in this sample |
| R01 vintage reserve (H100) | -7,629.39 → +991.13 | Capital-feedback support, fragile |
| M01 weakening two checks | -9,003.75 → -9,003.75 | Existing rule; no new contrast |
| M05 range confirmation | -21,099.81 → -18,741.32 | Both primary endpoints improve; still poor |
| M03 capped gap trail | -11,881.76 → -13,428.23 | Tails improve, normalized net worsens |
| R07 daily confirmation | +117.01 → +445.41 | Improved but LOW_SUPPORT/concentrated |

R01/M05/R07 improve both total net and exposure-normalized net. R01 H85 remains
+$10,488.39, substantially above the guarded H100. R01 guarded primary vintage
closures fall 223→40 per 832 original candidates, but TSLA/AVGO dominate gains.
R07 depends on AAPL/TSLA. M05 loses in every year, and risk closures rise.
This is mechanism diagnosis, not persistent alpha or a final strategy selection.

The funded replay took 146.33s including export;
engine 143.48s, peak RSS
1.340 GB. Exact final storage and tests are in
FINAL_DIAGNOSTIC_CONTENT_MANIFEST.json and VALIDATION_AND_INTEGRITY.md.

A small exporter omission of three OGN physical rows was recovered exactly from
the sealed 2021 checkpoint; account results never changed and no replay was used.
Per-candidate rejection reasons were not exported; original potential keys and
aggregate budget/duplicate/other rejection counts remain explicit. Further
financial or risk improvements cannot be inferred from an unfilled key alone.

Read MECHANISM_DECISION_TABLE.md, analysis_01/PAIRED_OPPORTUNITY_AND_EXIT_DIVERGENCE.csv,
and supplement_01/ for complete physical-cost and stress checks. The 449-portion
future-reference sample is non-funded and contains risk-infeasible extensions.

**Next:** separately authorized final-design meeting: review reserve mechanics,
range persistence versus weak raw edge, and gap-tail trade-offs against unchanged
controls; freeze a small slate before new testing. All 18 remain eligible.
Fresh prospective/untouched confirmation is required for strong claims.
No final algorithms selected, no S2-C risk overlay, no Stage6 independent audit.
