# P024 baseline forensics — PASS

Ledger44/200; zero optimizer updates. All1701 source/derived hashes match. Four role populations and both T2 checkpoint/prediction sets verified. Protected2026 files byte-hashed only.

Historical strict0.1% selector reproduces seed42 selected/raw7/7 and seed123 selected/raw1/12. At seed123 the raw improvement is approximately0.0714%, below0.1%. The0.025% replay selects12 on the available curve but remains right-censored: later epochs were never run. This is a checkpoint-rule motivation, not a counterfactual refit result.

Full tables: baseline_forensics.csv and baseline_selector_forensics.csv. Online train loss is transformed z-MSE with head dropoutON; selection loss is fixed-checkpoint original TG20 MSE with dropoutOFF. Clipping frequency and near-zero dispersion do not establish saturation, vanishing gradients or optimizer failure. Original scientific holds/backlog remain unchanged.
