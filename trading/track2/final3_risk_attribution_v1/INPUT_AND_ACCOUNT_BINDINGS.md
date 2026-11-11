# Input and account bindings

Canonical source: `trading/track2/final_directional_slate_v1/analysis_03`, backed by
`runs/sizing-matched-20261110-r1/results`. The final root content manifest validates
relevant inputs. `SOURCE_REGISTER_BEFORE.json` binds 26 paths with
SHA256, byte size, mtime, role and available row count. Model/protocol anchors are
hashed; no model weights or underlying market-source partitions are read.

`runs/analysis_01/ACCOUNT_BINDINGS.json` lists exact 12 case IDs, run ID, protocol hash, policy,
arm, population and all original Decimal terminal components. Joining uses the sealed
RESULTS `strategy_id + '_' + variant`; raw cohort `arm` is a book ID and `population`
is economic mode, so neither is used as an arm/sample key. Daily candidate/arm rows
are attached to the verified catalog after the 12-book/1,005-session check.

| Policy | Arm | Account ID | Net USD exact | Protocol SHA |
| --- | --- | --- | --- | --- |
| M04-T480 | EQUAL | M04_F3_MATCHED_EQUAL | 2606.125470588207486134418334 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| M04-T480 | ROLLING_RISK | M04_F3_MATCHED_ROLLING_RISK | 1717.999098238317333342341008 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| M04-T480 | EWMA_RISK | M04_F3_MATCHED_EWMA_RISK | -2567.512835803194260092595583 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| M04-T480 | S2C_RISK | M04_F3_MATCHED_S2C_RISK | -2036.513669297297265115284650 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| R01-A | EQUAL | R01_F1_MATCHED_EQUAL | -8981.084302744109589041095881 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| R01-A | ROLLING_RISK | R01_F1_MATCHED_ROLLING_RISK | -7968.607312993222983257229859 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| R01-A | EWMA_RISK | R01_F1_MATCHED_EWMA_RISK | -7703.253123042343987823439880 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| R01-A | S2C_RISK | R01_F1_MATCHED_S2C_RISK | -8276.065695899490106544901060 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| R07-PERSIST | EQUAL | R07_F4_MATCHED_EQUAL | 1895.015606146792237442922366 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| R07-PERSIST | ROLLING_RISK | R07_F4_MATCHED_ROLLING_RISK | 2984.091643650802891933028912 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| R07-PERSIST | EWMA_RISK | R07_F4_MATCHED_EWMA_RISK | 2318.843630403652968036529672 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |
| R07-PERSIST | S2C_RISK | R07_F4_MATCHED_S2C_RISK | 3111.776373326716133942161354 | 4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6 |

Primary population is MATCHED throughout. The 24-row source containers also hold
ATTAINABLE; those rows are excluded from paired financial analysis. Original readiness
counts are published separately in MATCHED_OPPORTUNITY_COUNTS.csv. Parent R01 H85
+$10,488.39 is not the matched EQUAL book: its causal opportunity population differs.
This task neither recomputes alpha eligibility nor changes its frozen availability.
