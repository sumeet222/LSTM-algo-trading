# P2.1 hand-checkable clock traces

Calendar metadata is real XNYS; all source observations below are **FAKE / SYNTHETIC**. Publication exactly at period end is a test fixture, not an Alpaca latency assumption. Proposed timestamps are not prices, labels or fills. Every issuance here is PLANNED_SYNTHETIC.

| Session | Origin | Cutoff ET | Issue ET | Planned entry → exit ET | Entry UTC | Schedule reason | Information reason | calendar_valid | source_asof_verified | G2 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2020-07-01 | 1 | 10:30 | 10:32 | 10:33 → 14:33 | 2020-07-01T14:33:00+00:00 | SCHEDULE_VALID | AVAILABLE_AT_CUTOFF | True | false | BLOCKED |
| 2020-07-01 | 2 | 11:30 | 11:32 | 11:33 → 15:33 | 2020-07-01T15:33:00+00:00 | SCHEDULE_VALID | AVAILABLE_AT_CUTOFF | True | false | BLOCKED |
| 2020-11-27 | 1 | 10:30 | 10:32 | 10:33 → 14:33 | 2020-11-27T15:33:00+00:00 | EXIT_OUTSIDE_SESSION | AVAILABLE_AT_CUTOFF | False | false | BLOCKED |
| 2020-01-02 | 1 | 10:30 | 10:32 | 10:33 → 14:33 | 2020-01-02T15:33:00+00:00 | SCHEDULE_VALID | AVAILABLE_AT_CUTOFF | True | false | BLOCKED |
| 2020-07-01 | 1 | 10:30 | 10:32 | 10:33 → 14:33 | 2020-07-01T14:33:00+00:00 | SCHEDULE_VALID | SOURCE_CLOCK_UNKNOWN | True | false | BLOCKED |

Ordinary six intervals:09:30–10:30,10:30–11:30,11:30–12:30,12:30–13:30,13:30–14:30,14:30–15:30 ET. Terminal stub15:30–16:00 excluded from complete-hour history; 15:33 execution time is not a feature-hour slot. 14:33−10:33=240min; 15:33−11:33=240min. Cutoff+2min issuance; ceil(issuance+1min) entry.

2020-11-27 closes13:00 ET/18:00 UTC:three full hours end10:30,11:30,12:30; stub12:30–13:00. Both candidate exits14:33/15:33 breach this real close. Proposed outside-session times remain diagnostic rejected proposals, with zero schedulable origins.

Winter2020-01-02:ET offset−05:00, entry10:33=15:33 UTC, exit14:33=19:33 UTC. Summer2020-07-01:ET offset−04:00, entry10:33=14:33 UTC, exit14:33=18:33 UTC. Local elapsed240 unchanged. Thanksgiving2020-11-26:NO_SESSION/no origins (automated test).

Actual delayed issuance10:34:30 (within5min)→earliest opening10:36→exit14:36. Inclusive5min boundary10:35→10:36→14:36;10:35:01 rejects ISSUANCE_TOO_LATE. No forced nominal exit. Downstream shifted-origin strategy treatment is unresolved. Every historical feature step still uses its own cutoff, not issuance.

Unknown-publication row retains valid calendar but rejects SOURCE_CLOCK_UNKNOWN. Synthetic availability just before a cutoff is accepted only under test_scenario=True and never verifies a real source. Source metadata assertions require review; there are no real publication clocks in this package. Entry eligibility, label validity and execution outcome remain null. F01 existing120min period-age/60min publication-age fixture rejects STALE_PERIOD_END independently of these stock-clock contracts.

Exact UTC keys, bases and boundaries (no source OHLCV):

```json
[
  {
    "session": "2020-07-01",
    "origin": 1,
    "symbol": "FAKE",
    "observation_id": "synthetic-2020-07-01-1",
    "native_label": "2020-07-01T13:30:00+00:00",
    "native_basis": "SYNTHETIC",
    "period_start": "2020-07-01T13:30:00+00:00",
    "period_end": "2020-07-01T14:30:00+00:00",
    "period_basis": "SYNTHETIC",
    "available_at": "2020-07-01T14:30:00+00:00",
    "availability_basis": "SYNTHETIC",
    "evidence_ref": null,
    "historical_step_cutoff": "2020-07-01T14:30:00+00:00",
    "forecast_cutoff": "2020-07-01T14:30:00+00:00",
    "issuance": "2020-07-01T14:32:00+00:00",
    "issuance_kind": "PLANNED_SYNTHETIC",
    "proposed_entry": "2020-07-01T14:33:00+00:00",
    "proposed_exit": "2020-07-01T18:33:00+00:00",
    "calendar_valid": true,
    "schedule_reason": "SCHEDULE_VALID",
    "information_reason": "AVAILABLE_AT_CUTOFF",
    "source_asof_verified": false,
    "scenario_only": true,
    "entry_eligible": null,
    "label_valid": null,
    "execution_outcome": null,
    "G2_status": "BLOCKED"
  },
  {
    "session": "2020-07-01",
    "origin": 2,
    "symbol": "FAKE",
    "observation_id": "synthetic-2020-07-01-2",
    "native_label": "2020-07-01T14:30:00+00:00",
    "native_basis": "SYNTHETIC",
    "period_start": "2020-07-01T14:30:00+00:00",
    "period_end": "2020-07-01T15:30:00+00:00",
    "period_basis": "SYNTHETIC",
    "available_at": "2020-07-01T15:30:00+00:00",
    "availability_basis": "SYNTHETIC",
    "evidence_ref": null,
    "historical_step_cutoff": "2020-07-01T15:30:00+00:00",
    "forecast_cutoff": "2020-07-01T15:30:00+00:00",
    "issuance": "2020-07-01T15:32:00+00:00",
    "issuance_kind": "PLANNED_SYNTHETIC",
    "proposed_entry": "2020-07-01T15:33:00+00:00",
    "proposed_exit": "2020-07-01T19:33:00+00:00",
    "calendar_valid": true,
    "schedule_reason": "SCHEDULE_VALID",
    "information_reason": "AVAILABLE_AT_CUTOFF",
    "source_asof_verified": false,
    "scenario_only": true,
    "entry_eligible": null,
    "label_valid": null,
    "execution_outcome": null,
    "G2_status": "BLOCKED"
  },
  {
    "session": "2020-11-27",
    "origin": 1,
    "symbol": "FAKE",
    "observation_id": "synthetic-2020-11-27-1",
    "native_label": "2020-11-27T14:30:00+00:00",
    "native_basis": "SYNTHETIC",
    "period_start": "2020-11-27T14:30:00+00:00",
    "period_end": "2020-11-27T15:30:00+00:00",
    "period_basis": "SYNTHETIC",
    "available_at": "2020-11-27T15:30:00+00:00",
    "availability_basis": "SYNTHETIC",
    "evidence_ref": null,
    "historical_step_cutoff": "2020-11-27T15:30:00+00:00",
    "forecast_cutoff": "2020-11-27T15:30:00+00:00",
    "issuance": "2020-11-27T15:32:00+00:00",
    "issuance_kind": "PLANNED_SYNTHETIC",
    "proposed_entry": "2020-11-27T15:33:00+00:00",
    "proposed_exit": "2020-11-27T19:33:00+00:00",
    "calendar_valid": false,
    "schedule_reason": "EXIT_OUTSIDE_SESSION",
    "information_reason": "AVAILABLE_AT_CUTOFF",
    "source_asof_verified": false,
    "scenario_only": true,
    "entry_eligible": null,
    "label_valid": null,
    "execution_outcome": null,
    "G2_status": "BLOCKED"
  },
  {
    "session": "2020-01-02",
    "origin": 1,
    "symbol": "FAKE",
    "observation_id": "synthetic-2020-01-02-1",
    "native_label": "2020-01-02T14:30:00+00:00",
    "native_basis": "SYNTHETIC",
    "period_start": "2020-01-02T14:30:00+00:00",
    "period_end": "2020-01-02T15:30:00+00:00",
    "period_basis": "SYNTHETIC",
    "available_at": "2020-01-02T15:30:00+00:00",
    "availability_basis": "SYNTHETIC",
    "evidence_ref": null,
    "historical_step_cutoff": "2020-01-02T15:30:00+00:00",
    "forecast_cutoff": "2020-01-02T15:30:00+00:00",
    "issuance": "2020-01-02T15:32:00+00:00",
    "issuance_kind": "PLANNED_SYNTHETIC",
    "proposed_entry": "2020-01-02T15:33:00+00:00",
    "proposed_exit": "2020-01-02T19:33:00+00:00",
    "calendar_valid": true,
    "schedule_reason": "SCHEDULE_VALID",
    "information_reason": "AVAILABLE_AT_CUTOFF",
    "source_asof_verified": false,
    "scenario_only": true,
    "entry_eligible": null,
    "label_valid": null,
    "execution_outcome": null,
    "G2_status": "BLOCKED"
  },
  {
    "session": "2020-07-01",
    "origin": 1,
    "symbol": "FAKE",
    "observation_id": "unknown-publication",
    "native_label": "2020-07-01T13:30:00+00:00",
    "native_basis": "SYNTHETIC",
    "period_start": "2020-07-01T13:30:00+00:00",
    "period_end": "2020-07-01T14:30:00+00:00",
    "period_basis": "SYNTHETIC",
    "available_at": null,
    "availability_basis": "UNKNOWN",
    "evidence_ref": null,
    "historical_step_cutoff": "2020-07-01T14:30:00+00:00",
    "forecast_cutoff": "2020-07-01T14:30:00+00:00",
    "issuance": "2020-07-01T14:32:00+00:00",
    "issuance_kind": "PLANNED_SYNTHETIC",
    "proposed_entry": "2020-07-01T14:33:00+00:00",
    "proposed_exit": "2020-07-01T18:33:00+00:00",
    "calendar_valid": true,
    "schedule_reason": "SCHEDULE_VALID",
    "information_reason": "SOURCE_CLOCK_UNKNOWN",
    "source_asof_verified": false,
    "scenario_only": true,
    "entry_eligible": null,
    "label_valid": null,
    "execution_outcome": null,
    "G2_status": "BLOCKED"
  }
]
```
