"""Candidate-only structural masks; unchanged FT0 math, no labels/fits/activation."""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from .aggregation import aggregate_session_hours
from .clocks import execution_plan
from .config import digest, fingerprint, write_json
from .ft0_audit import mechanical_m2
from .ft0_transforms import ORDER
from .labels import UNIVERSE
from .m2 import scheduled_window
from .remediation_overlay import history_from_view, native_timestamp
from .remediation_transport import read_chunk
from .stock_features import FeatureCalculator
from .stock_source import StockBar, StockCalendar, StockHistory, numeric
from .store import read_verified

PACKAGE = "TA-UNIVERSE-RETENTION-SCREEN-001"
BACKUPS = ("MSFT", "BAC", "MRK", "COST", "HON")
SECTORS = ("Technology", "Financials", "Healthcare", "Consumer staples", "Industrials")
FULL_MASK = (1 << 16) - 1
REMED = Path("reports/data_audit/ta_data_remed_ft0_001_2026-10-11_195135")


def verify_screen_authority() -> dict:
    """Verify inherited P2/P3 holds before diagnostic work, without clearing any."""
    from .p2_closure import load_deferred_work

    p2 = load_deferred_work(Path("configs/track_a_p2_engineering_handoff_v1.json"))
    api = json.loads(
        Path(
            "reports/data_audit/ta_p3_baselines_close_2026-10-12_004950/api_handoff.json"
        ).read_text()
    )
    ref = api["v2"]
    if digest(Path(ref["path"])) != ref["sha256"]:
        raise ValueError("P3_V2_REGISTER_SHA_REQUIRED")
    p3 = json.loads(Path(ref["path"]).read_text())["entries"]
    if (
        len(p2) != 16
        or len(p3) != 33
        or any(e["scientific_status"] != "HOLD" or not e["NO_AUTO_CLEAR"] for e in p3)
    ):
        raise ValueError("PERSISTENT_SCIENTIFIC_HOLDS_REQUIRED")
    return {"P2_entries": len(p2), "P3_entries": len(p3), "P3_sha": ref["sha256"]}


def validate_panel(symbols: tuple[str, ...]) -> None:
    if len(symbols) != 5 or len(set(symbols)) != 5:
        raise ValueError("ORDERED_FIVE_SLOT_PANEL_REQUIRED")
    if any(s not in (a, b) for s, a, b in zip(symbols, UNIVERSE, BACKUPS)):
        raise ValueError("PREDECLARED_SECTOR_SLOT_REQUIRED")


def panels() -> tuple[tuple[str, ...], ...]:
    return tuple(itertools.product(*zip(UNIVERSE, BACKUPS)))


def primary_native(*, stop: str = "2023-07-01", warmup: bool = False) -> tuple[pd.DataFrame, dict]:
    """Read only requested original partitions; confirmation Parquets are never opened."""
    if stop not in {"2023-07-01", "2024-07-01"}:
        raise ValueError("CONFIRMATION_ACCESS_FORBIDDEN")
    bound = pd.Timestamp(stop, tz="America/New_York").tz_convert("UTC")
    frames, refs = [], []
    for path in sorted(Path("data/raw/alpaca/track_a").glob("*.manifest.json")):
        meta = json.loads(path.read_text())
        params = meta["params"]
        if pd.Timestamp(params["start"]) >= bound:
            continue
        if pd.Timestamp(params["end"]) >= bound:
            raise ValueError("SOURCE_PARTITION_CROSSES_ALLOWED_BOUNDARY")
        data = path.with_name(path.name.replace(".manifest.json", ".parquet"))
        frame = read_verified(data, path, params)
        frame["native_source_id"] = [
            fingerprint([r.provenance_id, r.symbol, native_timestamp(r.timestamp).isoformat()])
            for r in frame.itertuples()
        ]
        frames.append(frame)
        refs.append({"path": str(data), "sha256": digest(data), "rows": len(frame)})
    if warmup:
        manifest = json.loads((REMED / "source_extension_manifest_v2.json").read_text())
        for chunk in manifest["chunks"]:
            if chunk["kind"] != "WARMUP":
                continue
            path, mp = Path(chunk["data_path"]), Path(chunk["manifest_path"])
            if digest(mp) != chunk["manifest_sha256"] or digest(path) != chunk["sha256"]:
                raise ValueError("WARMUP_MANIFEST_CHANGED")
            meta = json.loads(mp.read_text())
            result = read_chunk(path.parent, meta["params"])
            if result is None:
                raise ValueError("WARMUP_CHUNK_MISSING")
            frame, _ = result
            frame = frame[frame.timestamp < pd.Timestamp("2020-07-01T04:00Z")].copy()
            frame["native_source_id"] = [
                fingerprint(
                    [
                        "ALPACA",
                        chunk["sha256"],
                        chunk["request_hash"],
                        r.symbol,
                        native_timestamp(r.timestamp).isoformat(),
                    ]
                )
                for r in frame.itertuples()
            ]
            frames.append(frame)
            refs.append({"path": str(path), "sha256": digest(path), "rows": len(frame)})
    if not frames:
        raise ValueError("ORIGINAL_SOURCE_REQUIRED")
    combined = pd.concat(frames, ignore_index=True).sort_values(["symbol", "timestamp"])
    if combined.duplicated(["symbol", "timestamp"]).any():
        raise ValueError("DUPLICATE_NATIVE_KEY")
    return combined, {"sources": refs, "stop_exclusive": stop, "warmup": warmup}


def diagnostic_history(
    frame: pd.DataFrame, symbols: tuple[str, ...], start: str, stop: str
) -> tuple[StockHistory, dict]:
    """Ordinal alias adapter to immutable P2 names, with actual identities in source IDs.

    Only source-only masks may be consumed. No global UNIVERSE is changed and no
    fitted certificate, TG0 value or scientific availability is constructed.
    """
    validate_panel(symbols)
    if stop not in {"2023-06-30", "2024-06-30"}:
        raise ValueError("CONFIRMATION_FEATURE_ACCESS_FORBIDDEN")
    if set(frame.symbol) - set(symbols):
        raise ValueError("DIAGNOSTIC_UNREQUESTED_SYMBOL")
    if frame.duplicated(["symbol", "timestamp"]).any():
        raise ValueError("DUPLICATE_NATIVE_KEY")
    alias = dict(zip(symbols, UNIVERSE))
    mapped = frame.copy()
    mapped["symbol"] = mapped.symbol.map(alias)
    hours, qa = aggregate_session_hours(mapped, list(UNIVERSE), start, stop)
    cal = StockCalendar(start, stop)
    ids = {(r.symbol, r.timestamp): r.native_source_id for r in mapped.itertuples()}
    bars = []
    for r in hours.itertuples():
        if not isinstance(r.timestamp, pd.Timestamp) or not isinstance(
            r.available_at, pd.Timestamp
        ):
            raise ValueError("EXACT_NATIVE_TIMESTAMPS_REQUIRED")
        clock = cal.clock(str(r.session))
        slot = (
            0
            if r.is_stub
            else next(i for i, h in enumerate(clock.hours, 1) if h.end == r.available_at)
        )
        starts = pd.date_range(r.timestamp, r.available_at, freq="30min", inclusive="left")
        bars.append(
            StockBar(
                str(r.symbol),
                str(r.session),
                slot,
                r.timestamp,
                r.available_at,
                *(numeric(v) for v in (r.open, r.high, r.low, r.close, r.volume)),
                source_ids=tuple(str(ids[r.symbol, t]) for t in starts),
            )
        )
    history = StockHistory(cal, tuple(bars))
    history.binding = fingerprint([history.binding, PACKAGE, symbols, "ORDINAL_ALIAS_SOURCE_ONLY"])
    qa["identity"] = {
        "symbols": symbols,
        "alias": alias,
        "version": fingerprint([PACKAGE, symbols]),
    }
    return history, qa


def origin_masks(
    history: StockHistory,
    symbols: tuple[str, ...],
    *,
    first: str = "2020-07-01",
    stop: str = "2023-07-01",
) -> list[dict]:
    """Reuse original Components.coverage and mechanical M2 reference-presence rule."""
    validate_panel(symbols)
    if stop not in {"2023-07-01", "2024-07-01"}:
        raise ValueError("CONFIRMATION_ACCESS_FORBIDDEN")
    calc = FeatureCalculator(history)
    coverage = {}
    for alias in UNIVERSE:
        for step in history.calendar.steps:
            if step.session >= stop:
                break
            comp = calc.components(alias, step, source_only=True)
            coverage[alias, step.end] = comp.coverage
    rows, m2cache = [], {}
    for day, clock in history.calendar._sessions.items():
        if not first <= day < stop:
            continue
        for origin in (1, 2):
            if not execution_plan(clock, origin).calendar_valid:
                continue
            try:
                steps = scheduled_window(history.calendar, day, origin)
            except ValueError:
                steps = ()
            losses, masks, direct = {}, {}, {}
            for actual, alias in zip(symbols, UNIVERSE):
                bad: dict[str, dict] = {}
                missing = []
                if not steps:
                    bad = {c: {"reason": "SCHEDULED_HISTORY_INSUFFICIENT"} for c in ORDER}
                for step in steps:
                    if (alias, step.session, step.slot) not in history.bars:
                        missing.append([step.session, step.slot])
                    mk = alias, step.session, origin
                    if mk not in m2cache:
                        m2cache[mk] = mechanical_m2(history, alias, step.session, origin)
                    for c in ORDER:
                        good = m2cache[mk] if c == "M2" else coverage[alias, step.end][c]
                        if not good and c not in bad:
                            bad[c] = {
                                "session": step.session,
                                "slot": step.slot,
                                "cutoff": step.end.isoformat(),
                            }
                masks[actual] = sum(1 << i for i, c in enumerate(ORDER) if c not in bad)
                losses[actual] = bad
                direct[actual] = missing
            rows.append(
                {
                    "session": day,
                    "origin": origin,
                    "id": fingerprint([PACKAGE, day, origin]),
                    "masks": masks,
                    "failed_channels": losses,
                    "missing_48_steps": direct,
                    "mechanical_ft0": all(m == FULL_MASK for m in masks.values()),
                    "research_ready": False,
                }
            )
    return rows


def counterfactuals(rows: list[dict]) -> list[dict]:
    """32 perfect-mask upper bounds only: no prices, recovered rows or valid samples."""
    if len(rows) != 1502 or len({r["id"] for r in rows}) != 1502:
        raise ValueError("FIXED1502_TRAIN_ORIGINS_REQUIRED")
    result = []
    for bits in itertools.product((0, 1), repeat=5):
        removed = tuple(s for s, bit in zip(UNIVERSE, bits) if bit)
        passing = [
            r for r in rows if all(r["masks"][s] == FULL_MASK or s in removed for s in UNIVERSE)
        ]
        counts = {o: sum(r["origin"] == o for r in passing) for o in (1, 2)}
        result.append(
            {
                "removed_masks": removed,
                "count": len(removed),
                "upper_numerator": len(passing),
                "denominator": 1502,
                "fraction": len(passing) / 1502,
                "could_reach90": len(passing) >= 1352,
                "each_origin85": all(n / 751 >= 0.85 for n in counts.values()),
                "by_origin": counts,
                "sessions": len({r["session"] for r in passing}),
                "counterfactual_only": True,
                "recovered_or_trainable": False,
            }
        )
    return result


def gate_a(out: Path) -> dict:
    """Reconcile byte-bound old evidence and raw keys, then derive ticker/channel losses."""
    verify_screen_authority()
    original, source = primary_native()
    extended, ext_source = primary_native(warmup=True)
    old_hist, old_qa = history_from_view(
        original, "2020-07-01", view="ORIGINAL_SCREEN", end="2023-06-30"
    )
    ext_hist, ext_qa = history_from_view(
        extended, "2019-12-18", view="ALPACA_ONLY_EXTENDED", end="2023-06-30"
    )
    old_rows = origin_masks(old_hist, UNIVERSE)
    rows = origin_masks(ext_hist, UNIVERSE)
    old_count, count = (
        sum(r["mechanical_ft0"] for r in old_rows),
        sum(r["mechanical_ft0"] for r in rows),
    )
    if (len(old_rows), len(rows), old_count, count) != (1502, 1502, 919, 1183):
        raise ValueError("BASELINE_RETENTION_NOT_REPRODUCED")
    ledger = json.loads((REMED / "gap_cluster_reconciliation.json").read_text())
    observed = set(zip(original.symbol, original.timestamp))
    cluster_summary = []
    for c in ledger["clusters"]:
        symbol, day = c["symbol"], c["session"]
        clock = ext_hist.calendar.clock(day)
        assert clock.open is not None and clock.close is not None
        expected = set(pd.date_range(clock.open, clock.close, freq="30min", inclusive="left"))
        keys = [pd.Timestamp(k["start_UTC"]) for k in c["original_missing_keys"]]
        if any(t not in expected or (symbol, t) in observed for t in keys):
            raise ValueError("GAP_KEY_LEDGER_DIVERGENCE")
        actual = expected - {t for s, t in observed if s == symbol and t in expected}
        if actual != set(keys):
            raise ValueError("GAP_SESSION_LEDGER_DIVERGENCE")
        cluster_summary.append(
            {
                "symbol": symbol,
                "session": day,
                "missing_keys": [t.isoformat() for t in keys],
                "local_start_times": [
                    t.tz_convert("America/New_York").strftime("%H:%M") for t in keys
                ],
                "gap_minutes": len(keys) * 30,
                "session_kind": c["expected_session_kind"],
                "repeat_native_rows": c["Alpaca30Min_returned_rows"],
                "tight_minute_rows": c["minute_returned_rows"],
                "no_trade_claim": (
                    "NOT_ESTABLISHED; empty/filtered provider bars do not prove no trades"
                ),
                "evidence": str(REMED / "gap_cluster_reconciliation.json"),
            }
        )
    bounds = counterfactuals(rows)
    tickers = []
    for slot, s in enumerate(UNIVERSE):
        rejected = [r for r in rows if r["masks"][s] != FULL_MASK]
        direct = [r for r in rows if r["missing_48_steps"][s]]
        channels = Counter(c for r in rejected for c in r["failed_channels"][s])
        perfect = next(b for b in bounds if b["removed_masks"] == (s,))
        tickers.append(
            {
                "slot": slot,
                "sector": SECTORS[slot],
                "original": s,
                "backup": BACKUPS[slot],
                "missing_native_keys": sum(
                    len(c["missing_keys"]) for c in cluster_summary if c["symbol"] == s
                ),
                "direct48_train_origins": len(direct),
                "rejected_train_origins": len(rejected),
                "impacted_ids": [r["id"] for r in rejected],
                "channel_counts": dict(channels),
                "uniquely_unlocked_perfect_backup": perfect["upper_numerator"] - count,
                "single_replacement_upper_bound": perfect["upper_numerator"],
                "could_pass_single": perfect["could_reach90"],
                "lower_bound_no_verified_backup": count,
            }
        )
    priority = sorted(
        tickers,
        key=lambda t: (
            -t["uniquely_unlocked_perfect_backup"],
            -t["rejected_train_origins"],
            t["slot"],
        ),
    )
    write_json(out / "original_origin_masks.json", old_rows)
    write_json(out / "warmup_origin_masks.json", rows)
    write_json(
        out / "counterfactual_bounds.json",
        {
            "scope": "COUNTERFACTUAL_ONLY_NOT_RECOVERY",
            "original": counterfactuals(old_rows),
            "warmup": bounds,
        },
    )
    write_json(
        out / "candidate_priority.json",
        {
            "ranking_basis": (
                "TRAIN_ONLY_PERFECT_MASK_UNIQUE_UNLOCK_THEN_TOTAL_IMPACT_THEN_FIXED_SECTOR_SLOT"
            ),
            "frozen_before_development": True,
            "priority": priority,
            "all32_panels": [list(p) for p in panels()],
        },
    )
    result = {
        "package": PACKAGE,
        "status": "GATE_A_MECHANICAL_PASS_SCIENTIFIC_HOLD",
        "original": old_count,
        "warmup": count,
        "denominator": 1502,
        "required": 1352,
        "deficit": 1352 - count,
        "clusters": cluster_summary,
        "tickers": tickers,
        "unique_rejected_ids": [r["id"] for r in rows if not r["mechanical_ft0"]],
        "unique_direct48": sum(any(r["missing_48_steps"].values()) for r in rows),
        "overlap_warning": (
            "Ticker and indicator losses overlap; only union counts define panel retention."
        ),
        "source": source,
        "extended_source": ext_source,
        "qa_train_missing_keys": old_qa["missing_source_bars"],
        "mechanical_masks_no_floors_or_labels": True,
        "scientific_eligibility": False,
    }
    assert (
        len(cluster_summary) == 15 and sum(len(c["missing_keys"]) for c in cluster_summary) == 168
    )
    assert result["unique_direct48"] == 75 and len(result["unique_rejected_ids"]) == 319
    write_json(out / "original_gap_attribution.json", result)
    return result


def t2_absence_bound(
    calendar: StockCalendar, missing_daily_closes: tuple[str, ...], *, stop: str = "2023-07-01"
) -> list[dict]:
    """Necessary source-only T2 failures, assuming every OTHER daily close exists.

    No prices/returns are manufactured: only presence symbols are passed to the
    original 19/20 coverage predicate. This optimistic bound omits other channels,
    additional source gaps and causal approvals, so it cannot overstate losses.
    """
    from .stock_features import covered

    if stop != "2023-07-01" or any(day not in calendar.days for day in missing_daily_closes):
        raise ValueError("TRAIN_ONLY_KNOWN_DAILY_ABSENCE_REQUIRED")
    missing = set(missing_daily_closes)
    t2_good = {}
    for day in calendar.days:
        if day >= stop:
            break
        index = calendar.days.index(day)
        previous = calendar.days[max(0, index - 21) : index]
        changes = tuple(
            None if a in missing or b in missing else 1.0 for a, b in zip(previous, previous[1:])
        )
        t2_good[day] = covered(changes, 20, 19)
    failures = []
    for day, clock in calendar._sessions.items():
        if not "2020-07-01" <= day < stop:
            continue
        for origin in (1, 2):
            if not execution_plan(clock, origin).calendar_valid:
                continue
            steps = scheduled_window(calendar, day, origin)
            failed = next((step for step in steps if not t2_good[step.session]), None)
            if failed is not None:
                failures.append(
                    {
                        "session": day,
                        "origin": origin,
                        "id": fingerprint([PACKAGE, day, origin]),
                        "first_bad_T2_step": [failed.session, failed.slot],
                        "reason": "CONFIRMED_DAILY_CLOSE_ABSENCE_IMPLIES_LT19_OF20_T2",
                        "counterfactual_only": True,
                        "recovered_or_trainable": False,
                    }
                )
    return failures
