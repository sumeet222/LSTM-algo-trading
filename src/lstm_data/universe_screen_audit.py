"""Portable bounded pilot QA and optimistic source-presence impossibility proof."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pandas as pd

from .calendar import schedule
from .config import fingerprint, write_json
from .labels import UNIVERSE
from .stock_source import StockCalendar
from .universe_screen import (
    BACKUPS,
    FULL_MASK,
    PACKAGE,
    SECTORS,
    counterfactuals,
    panels,
    t2_absence_bound,
    verify_screen_authority,
)
from .universe_screen_source import ARCHIVE, read_backup_chunk


def analyze_pilot(report: Path) -> dict:
    """Use training absences only; unknown history stays optimistic, not recovered.

    Writes candidate-only proof, pilot QA and 32 hypothetical identities. No price
    is imputed and no backup's full retention is marked measured or eligible.
    """

    verify_screen_authority()

    def publish(path: Path, value: dict) -> None:
        if path.exists():
            if fingerprint(json.loads(path.read_text())) != fingerprint(value):
                raise ValueError("SCREEN_EVIDENCE_EXISTS_WITH_DIFFERENT_CONTENT")
        else:
            write_json(path, value)

    p = report
    pilot = json.loads((p / "backup_pilot_results.json").read_text())
    cal = StockCalendar("2019-12-18", "2023-06-30")
    formation = []
    native = []
    missing_closes = {s: [] for s in BACKUPS}
    frames = {}
    expected_days = tuple(
        pd.Timestamp(day).date().isoformat() for day in schedule("2020-04-06", "2020-06-30").index
    )
    assert len(expected_days) == 60
    for request in pilot["chunks"]:
        result = read_backup_chunk(ARCHIVE / request["kind"].lower(), request["params"])
        if result is None:
            raise ValueError("COMPLETE_PILOT_CHUNK_REQUIRED")
        f, m = result
        frames[request["hash"]] = f
        if request["kind"] == "FORMATION_DAILY":
            for s in BACKUPS:
                g = f[f.symbol == s]
                days = tuple(g.timestamp.dt.tz_convert("America/New_York").dt.date.astype(str))
                assert days == expected_days
                total = sum(Decimal(str(c)) * Decimal(str(v)) for c, v in zip(g.close, g.volume))
                avg = total / 60
                formation.append(
                    {
                        "symbol": s,
                        "sector_slot": SECTORS[BACKUPS.index(s)],
                        "expected": 60,
                        "received": len(g),
                        "unique": len(set(days)),
                        "sum_close_vendor_volume_USD": str(total),
                        "mean_USD": str(avg),
                        "threshold_USD": "50000000",
                        "proxy_numeric_pass": avg >= 50000000,
                        "status": "RETROSPECTIVE_PROXY_PASS_PIT_FORMATION_INCONCLUSIVE",
                        "historical_membership": (
                            "UNVERIFIED; SPY series substitution is not membership authorization"
                        ),
                        "actual_historical_publication": "UNKNOWN",
                        "source_request": request["hash"],
                        "source_chunk_sha256": m["sha256"],
                        "actual_rows_no_imputation": True,
                    }
                )
        if request["kind"] == "SIP_TIMING_GAP_PILOT":
            day = (
                pd.Timestamp(request["params"]["start"])
                .tz_convert("America/New_York")
                .date()
                .isoformat()
            )
            clock = cal.clock(day)
            assert clock.open is not None and clock.close is not None
            expect = set(pd.date_range(clock.open, clock.close, freq="30min", inclusive="left"))
            for s in BACKUPS:
                g = f[f.symbol == s]
                actual = set(g.timestamp)
                missing = sorted(expect - actual)
                if clock.close - pd.Timedelta(minutes=30) not in actual:
                    missing_closes[s].append(day)
                native.append(
                    {
                        "symbol": s,
                        "session": day,
                        "expected_RTH": len(expect),
                        "observed_RTH": len(expect & actual),
                        "missing_keys": [t.isoformat() for t in missing],
                        "daily_terminal_close_absent": clock.close - pd.Timedelta(minutes=30)
                        not in actual,
                        "off_grid_overlapping_keys": [
                            t.isoformat()
                            for t in actual
                            if clock.open <= t < clock.close and t not in expect
                        ],
                        "source_request": request["hash"],
                        "source_sha": m["sha256"],
                        "available_at": None,
                        "availability_basis": "UNKNOWN",
                    }
                )
    assert not any(r["off_grid_overlapping_keys"] for r in native)
    raw = next(r for r in pilot["chunks"] if r["kind"] == "RAW_SPLIT_CONTROL")
    split = next(
        r
        for r in pilot["chunks"]
        if r["kind"] == "SIP_TIMING_GAP_PILOT" and r["params"]["start"].startswith("2019-12-18")
    )
    a = frames[raw["hash"]].set_index(["symbol", "timestamp"])
    b = frames[split["hash"]].set_index(["symbol", "timestamp"])
    assert set(a.index) == set(b.index)
    control = []
    for s in BACKUPS:
        x = a.loc[s]
        y = b.loc[s]
        ratios = []
        for t in x.index:
            ratios.append(float(x.loc[t, "close"]) / float(y.loc[t, "close"]))
            # Report actual discrepancies; do not silently certify a conversion.
        control.append(
            {
                "symbol": s,
                "same_keys": len(x),
                "raw_per_split_close_ratio_min": min(ratios),
                "raw_per_split_close_ratio_max": max(ratios),
                "paired_close_times_volume_equivalence": "EXACT"
                if bool((x.close * x.volume == y.close * y.volume).all())
                else "INCONCLUSIVE_REQUIRES_ACTION_AND_ROUNDING_CONTRACT",
                "maximum_relative_product_error": float(
                    ((x.close * x.volume - y.close * y.volume).abs() / (x.close * x.volume)).max()
                ),
                "adjustment_scope": "split only, never dividend/spin-off",
                "historical_action_vintage": "UNVERIFIED",
            }
        )
    backup_losses = {
        s: t2_absence_bound(cal, tuple(sorted(set(days)))) for s, days in missing_closes.items()
    }
    original = json.loads((p / "warmup_origin_masks.json").read_text())
    counterfactuals(original)  # Refuse partial/duplicate denominator populations.
    orig_losses = {s: {r["id"] for r in original if r["masks"][s] != FULL_MASK} for s in UNIVERSE}
    comparison = []
    for names in panels():
        losses = set()
        for s in names:
            losses |= orig_losses[s] if s in UNIVERSE else {r["id"] for r in backup_losses[s]}
        count = 1502 - len(losses)
        actual = names == UNIVERSE
        comparison.append(
            {
                "symbols": names,
                "universe_version": fingerprint([PACKAGE, names]),
                "replacements": sum(s != a for s, a in zip(names, UNIVERSE)),
                "status": "MEASURED_ORIGINAL_BASELINE" if actual else "NOT_MEASURED_COMPLETE_PANEL",
                "formation_status": "PRIMARY_RESEARCHER_FIXED_RETROSPECTIVE_DISCLOSURE"
                if actual
                else "RETROSPECTIVE_PROXY_PASS_PIT_FORMATION_INCONCLUSIVE",
                "method": (
                    "Original full16-channel masks plus optimistic known-absence "
                    "T2-only backup masks"
                ),
                "retained_numerator": 1183 if actual else None,
                "denominator": 1502,
                "optimistic_retention_upper_numerator": count,
                "guaranteed_rejection_ids": sorted(losses),
                "guaranteed_rejects": len(losses),
                "could_reach1352": count >= 1352,
                "each_origin_upper_counts": {
                    o: sum(r["origin"] == o and r["id"] not in losses for r in original)
                    for o in (1, 2)
                },
                "scientific_status": "HOLD",
                "approval_status": "ORIGINAL_UNCHANGED"
                if actual
                else "REQUIRES_PROTOCOL_AMENDMENT",
                "proposal_scope": "PROPOSED_DATA_USABILITY_SENSITIVITY",
                "development_used_for_selection": False,
                "future_labels_computed": False,
            }
        )
    assert all(not r["could_reach1352"] for r in comparison)
    # Reconcile the presence-only bound with exact original T2 masks on the same three gap days.
    for s in ("JPM", "JNJ"):
        confirmed = tuple(
            c["session"]
            for c in json.loads((p / "original_gap_attribution.json").read_text())["clusters"]
            if c["symbol"] == s and c["local_start_times"][-1] == "15:30"
        )
        guaranteed = {r["id"] for r in t2_absence_bound(cal, confirmed)}
        real = {r["id"] for r in original if "T2" in r["failed_channels"][s]}
        assert guaranteed == real
    publish(
        p / "backup_source_qa_v2.json",
        {
            "status": "PILOT_SOURCE_QA_COMPLETE_FULL_HISTORY_NOT_ACQUIRED",
            "formation": formation,
            "pilot_RTH": native,
            "adjustment_controls": control,
            "actual_attempts": pilot["attempts"],
            "same_page_exception": str(p / "formation_transport_exception_v1.json"),
            "unverified_adjustment_controls": sum(
                c["paired_close_times_volume_equivalence"] != "EXACT" for c in control
            ),
            "correction_to_preliminary_qa": (
                "v1 incorrectly tagged every coupled-volume control PASS. v2 "
                "records the observed HON discrepancy; no source acquisition follows this analysis."
            ),
            "retrospective_98_95_full_history_coverage": "NOT_MEASURED",
            "source_availability": "UNKNOWN",
            "bulk_stop_reason": (
                "All32panels cannot reach90% even with every unobserved backup "
                "close present; more history cannot change this threshold decision."
            ),
            "SPY_redownloaded": False,
            "no_confirmation_rows_read": True,
        },
    )
    publish(
        p / "backup_known_absence_bounds.json",
        {
            "scope": "OPTIMISTIC_T2_ONLY_SOURCE_PRESENCE_BOUND_NOT_COMPLETE_RETENTION",
            "missing_daily_closes": missing_closes,
            "backup_guaranteed_T2_losses": backup_losses,
            "original_JPM_JNJ_T2_exact_equivalence": "PASS",
            "no_prices_or_returns_or_targets_created": True,
        },
    )
    publish(
        p / "candidate_universe_retention.json",
        {
            "status": "ALL32_THRESHOLD_IMPOSSIBLE_UNDER_CURRENT_OBSERVED_SOURCE",
            "panels": comparison,
            "measured_backup_complete_panels": 0,
            "development": "NOT_MEASURED_FOR_BACKUPS; original496/496SHA-bound disclosure only",
            "scientific_status": "HOLD",
            "original_universe_unchanged": True,
            "minimum_actual_passing_replacements": None,
            "training_only_decision_frozen": True,
        },
    )
    return {
        "minimum_backup_T2_losses": {s: len(v) for s, v in backup_losses.items()},
        "best_any_panel_upper": max(r["optimistic_retention_upper_numerator"] for r in comparison),
        "all32_90percent_impossible": True,
    }
