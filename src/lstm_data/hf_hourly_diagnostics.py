"""Non-model source/action diagnostics and bounded cached-Alpaca overlap checks."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .calendar import schedule
from .config import write_json


def nominal_interval_diagnostics(frame: pd.DataFrame, out: Path) -> dict:
    """Separate an outside-RTH start from a nominal hour that partially overlaps RTH."""
    wall = frame.datetime.dt.tz_localize(None)
    days = wall.dt.strftime("%Y-%m-%d")
    times = frame.datetime.dt.tz_convert("UTC")
    calendar = schedule(str(days.min()), str(days.max()))
    opens = {str(pd.Timestamp(str(day)).date()): row.open for day, row in calendar.iterrows()}
    closes = {str(pd.Timestamp(str(day)).date()): row.close for day, row in calendar.iterrows()}
    opening = pd.to_datetime(days.map(opens), utc=True)
    closing = pd.to_datetime(days.map(closes), utc=True)
    end = times + pd.Timedelta(hours=1)
    diagnostics = pd.DataFrame(
        dict(
            symbol=frame.symbol,
            month=days.str[:7],
            start_before_open_but_hour_overlaps=times.lt(opening) & end.gt(opening),
            start_before_close_but_nominal_end_overruns=times.lt(closing) & end.gt(closing),
            nominal_hour_wholly_inside_RTH=times.ge(opening) & end.le(closing),
            start_outside_RTH=times.lt(opening) | times.ge(closing),
            noncalendar_start=opening.isna(),
        )
    )
    columns = list(diagnostics.columns[2:])
    diagnostics.groupby(["symbol", "month"])[columns].sum().reset_index().to_csv(
        out / "nominal_interval_partial_overlap.csv", index=False
    )
    result = dict(
        counts={col: int(diagnostics[col].sum()) for col in columns},
        caveat=(
            "End=start+1h is nominal only. Terminal rows may be clipped stubs; "
            "observed duration/trades are not supplied. "
            "Outside-RTH START is not proof of outside-RTH trades."
        ),
    )
    write_json(out / "nominal_interval_interpretation.json", result)
    return result


def action_diagnostics(frame: pd.DataFrame, authority: dict, out: Path) -> dict:
    rows, jumps = ([], [])
    for symbol, g in frame.groupby("symbol", sort=True):
        g = g.sort_values("datetime").copy()
        g["day"] = g.datetime.dt.tz_localize(None).dt.strftime("%Y-%m-%d")
        ratio = g.close / g.close.shift(1)
        suspicious = np.abs(np.log(ratio)) > np.log(1.5)
        for row in g.loc[suspicious].head(20).index:
            jumps.append(
                dict(
                    symbol=symbol,
                    timestamp=str(g.loc[row, "datetime"]),
                    adjacent_close_ratio=float(ratio.loc[row]),
                    interpretation="SOURCE_DISCONTINUITY_CANDIDATE_NOT_A_TARGET_OR_INVALIDITY_VERDICT",
                )
            )
        for event in authority["events"]:
            if event["symbol"] != symbol:
                continue
            day = event["first_post_split_trading_date"]
            before, after = (g.loc[g.day < day], g.loc[g.day >= day])
            if before.empty or after.empty:
                rows.append(dict(**event, status="NO_EVENT_BOUNDARY_COVERAGE"))
                continue
            pre, post = (before.iloc[-1], after.iloc[0])
            previous_days = sorted(before.day.unique())[-5:]
            following_days = sorted(after.day.unique())[:5]
            pre_vol = float(before.loc[before.day.isin(previous_days), "volume"].median())
            post_vol = float(after.loc[after.day.isin(following_days), "volume"].median())
            rows.append(
                dict(
                    **event,
                    status="DESCRIPTIVE_ONLY_PARITY_UNVERIFIED",
                    last_pre_ET=str(pre.datetime),
                    first_post_ET=str(post.datetime),
                    open_to_previous_close_ratio=float(post.open / pre.close),
                    close_adj_to_close_pre=float(pre.close_adj / pre.close),
                    close_adj_to_close_post=float(post.close_adj / post.close),
                    median_hourly_volume_post_over_pre=post_vol / pre_vol if pre_vol > 0 else None,
                    caution=(
                        "Smooth prices do not establish all-OHLC/volume adjustment "
                        "parity; activity changes confound volume ratios"
                    ),
                )
            )
    pd.DataFrame(rows).to_csv(out / "corporate_action_boundary_checks.csv", index=False)
    pd.DataFrame(jumps).to_csv(out / "large_source_discontinuities.csv", index=False)
    identities = []
    for symbol in sorted(frame.symbol.unique()):
        record = authority["identity_cautions"].get(
            symbol,
            {
                "event": "Date-specific entity/sector/membership history UNVERIFIED",
                "source": "Dataset provides ticker only",
            },
        )
        identities.append(dict(symbol=symbol, point_in_time_identity_verified=False, **record))
    pd.DataFrame(identities).to_csv(out / "issuer_identity_cautions.csv", index=False)
    result = dict(
        close_adj_is_close_in_all_rows=bool(frame.close_adj.eq(frame.close).all()),
        checked_action_boundaries=len(rows),
        discontinuity_candidates_saved=len(jumps),
        dividend_adjustment="UNVERIFIED; no separate dividend-adjusted series observed",
        volume_adjustment="UNVERIFIED; no action factors or volume-inversion ledger",
        source_code=(
            "Publisher backfill copies close to close_adj if missing; "
            "client clamps high/low to observed OHLC extrema; no explicit"
            " adjust argument in SDK request"
        ),
        publication_timing=(
            "UNKNOWN; observed interval starts and "
            "reconstruction/retrieval dates are not available_at"
        ),
        action_vintage=("RETROSPECTIVE; no point-in-time action factors or restatement diff"),
        rights=("RIGHTS_UNRESOLVED; card MIT and underlying provider restrictions are separate"),
        underlying_terms="https://twelvedata.com/terms",
        model_training=False,
    )
    write_json(out / "corporate_actions_units_and_rights.json", result)
    return result


def cached_overlap(frame: pd.DataFrame, out: Path, root: Path) -> dict:
    """Read only six legal preconfirmation source dates; never query an external provider."""
    from .visualization.loaders import Catalog, ViewUnavailable, source_bars

    samples = (
        ("AAPL", "2020-08-31"),
        ("AAPL", "2024-01-16"),
        ("COST", "2023-10-27"),
        ("COST", "2024-01-16"),
        ("SBUX", "2023-10-27"),
        ("SBUX", "2024-01-16"),
    )
    if any((day >= "2024-07-01" for _, day in samples)):
        raise ValueError("ORIGINAL_CONFIRMATION_READ_DENIED")
    catalog = Catalog.discover(root)
    rows = []
    failures = []
    for symbol, day in samples:
        try:
            source, meta = source_bars(catalog, symbol, day, day)
        except ViewUnavailable as exc:
            failures.append(dict(symbol=symbol, day=day, error=str(exc)))
            continue
        hf = frame.loc[
            frame.symbol.eq(symbol)
            & frame.datetime.dt.tz_localize(None).dt.normalize().eq(pd.Timestamp(day))
        ]
        for slot in (0, 1):
            start = pd.Timestamp(day + " 09:30", tz="America/New_York") + pd.Timedelta(hours=slot)
            keys = pd.DatetimeIndex([start, start + pd.Timedelta(minutes=30)]).tz_convert("UTC")
            native = source.loc[source.timestamp.isin(keys)].sort_values("timestamp")
            matching = hf.loc[hf.datetime.eq(start)]
            if len(native) != 2 or len(matching) != 1 or native.timestamp.nunique() != 2:
                failures.append(
                    dict(
                        symbol=symbol,
                        day=day,
                        slot=slot + 1,
                        error="EXACT_CONSTITUENTS_OR_HF_START_ABSENT",
                    )
                )
                continue
            observed = matching.iloc[0]
            values = dict(
                open=float(native.open.iloc[0]),
                high=float(native.high.max()),
                low=float(native.low.min()),
                close=float(native.close.iloc[-1]),
                volume=float(native.volume.sum()),
            )
            row: dict[str, str | int | float | None] = dict(
                symbol=symbol,
                interval_start_ET=str(start),
                interval_end_ET=str(start + pd.Timedelta(hours=1)),
                observed_half_hours=2,
                HF_timeframe="1h",
                Alpaca_source="split-price / inverse-volume cached SIP30Min",
                interpretation=(
                    "Same nominal interval; vendor/adjustment/coverage "
                    "differences not a truth verdict"
                ),
            )
            for column, value in values.items():
                number = float(observed[column])
                row[column + "_HF_over_cached_Alpaca"] = number / value if value else None
                row[column + "_relative_difference"] = (number - value) / value if value else None
            rows.append(row)
    pd.DataFrame(rows).to_csv(out / "cached_alpaca_overlap_checks.csv", index=False)
    result = dict(
        examples=len(rows),
        unavailable=failures,
        original_confirmation_rows=0,
        provider_requests=0,
        existing_source_writes=0,
        limitation=(
            "Alpaca is not independently certified truth; feeds, "
            "revisions and action conventions may differ"
        ),
    )
    write_json(out / "cached_overlap_scope.json", result)
    return result
