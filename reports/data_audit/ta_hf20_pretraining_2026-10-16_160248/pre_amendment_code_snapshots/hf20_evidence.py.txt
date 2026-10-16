"""Bounded pre-held-out source/action and cached-only repair evidence."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from .config import digest, write_json
from .hf20_source import BARRIER, SYMBOLS
from .hf_hourly_audit import calendar_grid

ACTIONS = (
    ("AMZN", "2022-06-06", 20, "https://ir.aboutamazon.com/faqs/default.aspx"),
    (
        "TSLA",
        "2022-08-25",
        3,
        "https://ir.tesla.com/press-release/tesla-announces-three-one-stock-split",
    ),
    (
        "AVGO",
        "2024-07-15",
        10,
        (
            "https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-second-quarter-fiscal-year-2024-financial",
        ),
    ),
)


def source_evidence(frame: pd.DataFrame, bad: pd.DataFrame, out: Path) -> None:
    """Diagnostic ratios only, no return labels, source adjustments or overwrites."""
    if frame.datetime.ge(BARRIER).any():
        raise ValueError("HF20_PROTECTED_SOURCE_DIAGNOSTICS_DENIED")
    grid, _ = calendar_grid(str(frame.session.min()), str(frame.session.max()))
    frame = frame.loc[frame.UTC.isin(grid.loc[~grid.stub, "start"])].copy()
    # Tolerances are declared before reading any candidate or neighbor values.
    protocol = dict(
        close_median_relative_tolerance=0.001,
        OHLC_median_relative_tolerance=0.002,
        volume_median_relative_tolerance=0.05,
        required_neighbors_before=3,
        required_neighbors_after=3,
        price_factor=1.0,
        volume_factor=1.0,
        fitting_factors_authorized=False,
        status="DIAGNOSTIC_ONLY_NO_REPAIR_AUTHORITY",
    )
    write_json(out / "repair_comparison_protocol.json", protocol)
    rows = []
    for symbol, day, ratio, authority in ACTIONS:
        sample = frame.loc[frame.symbol.eq(symbol)]
        before = sample.loc[sample.session.lt(day)].tail(6)
        after = sample.loc[sample.session.ge(day)].head(6)
        rows.append(
            dict(
                symbol=symbol,
                first_split_trading_date=day,
                official_ratio=ratio,
                authority=authority,
                pre_rows=len(before),
                post_rows=len(after),
                open_over_previous_close=float(after.open.iloc[0] / before.close.iloc[-1]),
                close_adj_over_close_before=float(
                    before.close_adj.iloc[-1] / before.close.iloc[-1]
                ),
                close_adj_over_close_after=float(after.close_adj.iloc[0] / after.close.iloc[0]),
                median_volume_post_over_pre=float(after.volume.median() / before.volume.median()),
                interpretation="DESCRIPTIVE_NOT_ADJUSTMENT_OR_SHARE_UNIT_PROOF",
            )
        )
    pd.DataFrame(rows).to_csv(out / "action_boundary_diagnostics.csv", index=False)
    # Search metadata only for the exact defect months; never read old confirmation candles.
    candidates = []
    neighbors = []
    cache_refs = []
    for defect in bad.itertuples():
        key = pd.Timestamp(str(defect.interval_start_UTC))
        if key >= BARRIER:
            candidates.append(
                dict(
                    symbol=defect.symbol,
                    session=defect.session,
                    status="PROTECTED_KEY_ONLY_NO_PROVIDER_COMPARISON",
                )
            )
            continue
        if str(defect.session) >= "2024-07-01":
            raise ValueError("LEGACY_CONFIRMATION_COMPARISON_DENIED")
        matches = []
        for path in Path("data/raw/alpaca").rglob(str(defect.session)[:7] + "*.manifest.json"):
            meta = json.loads(path.read_text())
            symbols = meta.get("config", {}).get("symbols", [])
            if defect.symbol in symbols and meta.get("config", {}).get("timeframe") == "30Min":
                matches.append((path, meta))
        if not matches:
            candidates.append(
                dict(
                    symbol=defect.symbol,
                    session=defect.session,
                    status="NO_EXACT_SYMBOL_MONTH_IN_AUTHORIZED_CACHE",
                )
            )
            continue
        path, meta = matches[0]
        raw = path.with_suffix("").with_suffix(".parquet")
        if digest(raw) != meta["sha256"]:
            raise ValueError("CACHED_REFERENCE_HASH_CHANGED")
        start = key - pd.Timedelta(days=4)
        stop = key + pd.Timedelta(days=4)
        if stop >= pd.Timestamp("2024-07-01", tz="UTC"):
            raise ValueError("LEGACY_CONFIRMATION_COMPARISON_DENIED")
        cached = pq.read_table(
            raw,
            columns=["symbol", "timestamp", "open", "high", "low", "close", "volume"],
            filters=[
                ("symbol", "=", defect.symbol),
                ("timestamp", ">=", start.to_pydatetime()),
                ("timestamp", "<", stop.to_pydatetime()),
            ],
        ).to_pandas()
        hf = frame.loc[frame.symbol.eq(defect.symbol) & frame.UTC.between(start, stop)]
        hf = pd.concat([hf.loc[hf.UTC.lt(key)].tail(3), hf.loc[hf.UTC.gt(key)].head(3)])
        for observed in hf.itertuples():
            observed_time = pd.Timestamp(str(observed.UTC))
            constituents = cached.loc[
                cached.timestamp.isin([observed_time, observed_time + pd.Timedelta(minutes=30)])
            ].sort_values("timestamp")
            if len(constituents) != 2 or constituents.timestamp.nunique() != 2:
                continue
            values = dict(
                open=float(constituents.open.iloc[0]),
                high=float(constituents.high.max()),
                low=float(constituents.low.min()),
                close=float(constituents.close.iloc[-1]),
                volume=float(constituents.volume.sum()),
            )
            comparison: dict[str, str | int | float | None] = dict(
                symbol=str(defect.symbol),
                defect_start_UTC=str(key),
                neighbor_start_UTC=str(observed.UTC),
                side="before" if observed_time < key else "after",
                constituents=2,
                interval_status="MATCHED_NOMINAL_START_END_ONLY_VENDOR_SEMANTICS_CONDITIONAL",
            )
            for field, value in values.items():
                comparison[field + "_HF_over_Alpaca"] = (
                    float(getattr(observed, field) / value) if value else None
                )
            neighbors.append(comparison)
        cache_refs.append(
            dict(
                path=str(raw), sha256=digest(raw), manifest=str(path), manifest_sha256=digest(path)
            )
        )
        candidates.append(
            dict(
                symbol=defect.symbol,
                session=defect.session,
                status="CACHED_CANDIDATE_PRESENT_NO_INDEPENDENT_VOLUME_OR_HF_INTERVAL_CERTIFICATE",
                cache=str(raw),
                repair_accepted=False,
            )
        )
    pd.DataFrame(candidates).to_csv(out / "repair_candidates.csv", index=False)
    pd.DataFrame(neighbors).to_csv(out / "matched_cached_neighbors.csv", index=False)
    decisions = bad.copy()
    decisions["decision"] = "MASK_NO_PROVEN_MIXED_SOURCE_OVERLAY"
    decisions.to_csv(out / "repair_decisions.csv", index=False)
    decisions.to_csv(out / "unresolved_hours.csv", index=False)
    pd.DataFrame(
        columns=[
            "symbol",
            "interval_start_UTC",
            "interval_end_UTC",
            "provider",
            "original_sha256",
            "secondary_sha256",
            "constituent_keys",
            "price_factor",
            "volume_factor",
            "reason",
            "approval_id",
            "code_sha256",
            "repaired",
        ]
    ).to_csv(out / "repaired_hour_overrides.csv", index=False)
    write_json(
        out / "repair_decisions.json",
        dict(
            overrides=0,
            missing_hours=len(bad),
            provider_requests=0,
            cached_sources=cache_refs,
            not_vendor_pure_if_future_overlay=True,
            decision="Keep all six absent hours missing; no price/volume fabrication",
        ),
    )
    (out / "cross_provider_alignment.md").write_text(
        "# Cached-only alignment and repair decision\n\nSix exact missing HF keys were "
        "investigated. "
        "No override is accepted. See repair_candidates.csv and matched_cached_neighbors.csv. "
        "Two native cached30-minute rows can match the nominal HF interval, but this does not "
        "independently certify HF aggregation or share-volume units. No scaling factor was fitted. "
        "Tolerances were frozen in repair_comparison_protocol.json before reading candidates. "
        "Three before/three after neighbors are requested where present; actual counts "
        "remain explicit. "
        "No provider API request, paid access or legacy-confirmation numeric read.\n"
    )
    (out / "source_comparison_and_adjustments.md").write_text(
        (out / "cross_provider_alignment.md").read_text()
    )
    (out / "corporate_action_and_volume_basis.md").write_text(
        "# Action and share-volume basis\n\n[Provider "
        "support](https://support.twelvedata.com/en/articles/5179064-are-the-prices-adjus"
        "ted) "
        "describes intraday prices as unadjusted, unlike the HF card adjusted-close description. "
        "The pinned HF snapshot has close_adj==close; publisher fallback and OHLC clamping do not "
        "authenticate a corporate-action methodology. Issuer-confirmed AMZN/TSLA/AVGO split dates "
        "and bounded descriptive ratios are in action_boundary_diagnostics.csv; no "
        "factors were applied. "
        "Continuous observed prices do not independently establish volume or dividend adjustment. "
        "Only an actual researcher-approved as-reported retrospective price/share-volume "
        "assumption "
        "can support conditional preparation. No total-return or raw-share wealth "
        "accounting claim. "
        "Demonstrated unreconciled price-unit breaks require quarantine, never target clipping. "
        "This is not a complete action ledger or PIT vintage certificate.\n"
    )
    sectors = json.loads(Path("configs/hf_twelvedata_hourly_audit_v3.json").read_text())[
        "publisher_sector_etfs"
    ]
    pd.DataFrame(
        [
            dict(
                symbol=s,
                sector_proxy=sectors[s],
                issuer_identity="Publisher current ticker; historical entity mapping unverified",
            )
            for s in SYMBOLS
        ]
    ).to_csv(out / "cohort_issuer_sector.csv", index=False)
    liquid = frame.groupby("symbol").agg(
        rows=("symbol", "size"), median_observed_hour_volume=("volume", "median")
    )
    dollar = frame.close * frame.volume
    liquid["median_observed_hour_dollar_volume"] = dollar.groupby(frame.symbol).median()
    liquid.to_csv(out / "historical_liquidity_description.csv")
