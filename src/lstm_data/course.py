"""Byte-preserving course CSV inspection and compact Markdown evidence."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .calendar import schedule
from .config import atomic_new, digest, now, write_json
from .validation import OHLCV, defects, normalize


def audit_course(path: Path, provider: str, start: str, end: str) -> tuple[pd.DataFrame, dict]:
    """Independently inspect the entire file, including rows beyond its named end date."""
    if not path.is_file():
        raise FileNotFoundError(f"Course CSV absent: {path.name}; see data/README.md")
    before = digest(path)
    raw = pd.read_csv(path)
    if list(raw.columns) != ["timestamp", *OHLCV]:
        raise ValueError("Expected course schema timestamp,open,high,low,close,volume")
    frame = normalize(raw)
    timestamps = frame.timestamp.sort_values().reset_index(drop=True)
    local = timestamps.dt.tz_convert("America/New_York")
    gaps = timestamps.diff().dropna().dt.total_seconds() / 3600
    sessions = schedule(start, end)
    rth = pd.Series(False, index=timestamps.index)
    for _, row in sessions.iterrows():
        rth |= (timestamps >= row.open) & (timestamps < row.close)
    days = [
        "2020-07-01",
        "2020-11-01",
        "2020-11-02",
        "2020-11-27",
        "2021-03-14",
        "2021-03-15",
        "2025-06-30",
        "2025-07-01",
    ]
    examples = {}
    for day in days:
        mask = local.dt.strftime("%Y-%m-%d") == day
        examples[day] = [
            {"utc": utc.isoformat(), "new_york": eastern.isoformat()}
            for utc, eastern in zip(timestamps[mask], local[mask], strict=True)
        ]
    largest = gaps.nlargest(12)
    after = digest(path)
    if after != before:
        raise RuntimeError("Source changed during inspection; discard this audit and retry")
    audit = {
        "created_at": now(),
        "source_filename": path.name,
        "provider": provider,
        "retrieval_date": "unknown; researcher supplied file",
        "sha256": before,
        "size_bytes": path.stat().st_size,
        "rows": len(frame),
        "schema": {k: str(v) for k, v in frame.dtypes.items()},
        "earliest_utc": str(timestamps.min()),
        "latest_utc": str(timestamps.max()),
        "earliest_new_york": str(local.iloc[0]),
        "latest_new_york": str(local.iloc[-1]),
        "defects": defects(frame),
        "timestamp_semantics": "unknown",
        "corporate_action_policy": "unknown; course index instrument",
        "volume_semantics": "unknown; fractional values are not equity exchange share volume",
        "rth_timestamp_count": int(rth.sum()),
        "outside_rth_timestamp_count": int((~rth).sum()),
        "outside_named_local_dates": int(
            ((local.dt.strftime("%Y-%m-%d") < start) | (local.dt.strftime("%Y-%m-%d") > end)).sum()
        ),
        "utc_hour_counts": {
            str(k): int(v) for k, v in timestamps.dt.hour.value_counts().sort_index().items()
        },
        "new_york_hour_counts": {
            str(k): int(v) for k, v in local.dt.hour.value_counts().sort_index().items()
        },
        "new_york_weekday_counts": {
            str(k): int(v) for k, v in local.dt.day_name().value_counts().items()
        },
        "utc_offset_counts": {
            str(k): int(v)
            for k, v in local.map(lambda t: str(t.utcoffset())).value_counts().items()
        },
        "gap_hours_counts": {str(k): int(v) for k, v in gaps.value_counts().sort_index().items()},
        "largest_gaps": [
            {
                "previous_utc": timestamps.loc[idx - 1].isoformat(),
                "next_utc": timestamps.loc[idx].isoformat(),
                "hours": float(gap),
            }
            for idx, gap in largest.items()
        ]
        if timestamps.index.equals(pd.RangeIndex(len(timestamps)))
        else [],
        "volume_range": {"min": float(frame.volume.min()), "max": float(frame.volume.max())},
        "price_range": {
            "min": float(frame[OHLCV[:4]].min().min()),
            "max": float(frame[OHLCV[:4]].max().max()),
        },
        "representative_days": examples,
        "sidecar_files": sorted(
            p.name
            for p in path.parent.iterdir()
            if p.is_file() and p != path and not p.name.startswith(".")
        ),
        "gap_interpretation": "Observed gaps only; upstream instrument calendar is unknown. "
        "Weekend breaks are not automatically missing observations.",
    }
    return frame, audit


def course_markdown(audit: dict) -> str:
    lines = [
        "# Course USA500 source audit",
        "",
        "Original CSV bytes preserved.",
        "",
        "| Property | Observed |",
        "|---|---|",
    ]
    for key in (
        "source_filename",
        "sha256",
        "size_bytes",
        "rows",
        "earliest_utc",
        "latest_utc",
        "earliest_new_york",
        "latest_new_york",
        "rth_timestamp_count",
        "outside_rth_timestamp_count",
        "outside_named_local_dates",
        "timestamp_semantics",
    ):
        lines.append(f"| {key} | {audit[key]} |")
    lines += [
        "",
        f"Validation counts: `{audit['defects']}`.",
        "",
        "RTH counts classify timestamps only; they do not prove bar intervals or availability. "
        "The filename's final date must not be used as proof of the last bar's stock session.",
        "",
        "## Observation times and gaps",
        "",
        f"New York weekdays: `{audit['new_york_weekday_counts']}`.",
        "",
        f"UTC offsets: `{audit['utc_offset_counts']}`.",
        "",
        "| Gap hours | Count |",
        "|---|---|",
    ]
    lines += [f"| {hours} | {count} |" for hours, count in audit["gap_hours_counts"].items()]
    lines += ["", "| New York hour | Count |", "|---|---|"]
    lines += [f"| {hour} | {count} |" for hour, count in audit["new_york_hour_counts"].items()]
    lines += ["", "## Representative days (UTC and local offsets)", ""]
    for day, rows in audit["representative_days"].items():
        lines += [f"### {day}", "", "| UTC | America/New_York |", "|---|---|"]
        lines += [f"| {row['utc']} | {row['new_york']} |" for row in rows]
        if not rows:
            lines += ["| No observations | No observations |"]
        lines += [""]
    lines += [
        "## Provenance and decisions needed",
        "",
        f"Provider: {audit['provider']}. Retrieval date, upstream calendar, adjustment policy "
        "and timestamp semantics were not supplied. No definitive provider metadata is "
        f"embedded in the CSV schema. Other files in the source folder: {audit['sidecar_files']}.",
        "",
        f"Price range: {audit['price_range']}; volume range: {audit['volume_range']}.",
        "",
        "Fractional/zero volume requires source interpretation; it is not assumed to represent "
        "exchange share volume. Gaps require the source trading schedule before being labeled "
        "unexpected. Sunday/overnight data and DST differences are preserved.",
        "",
        "Index values are blocked from model use pending verified/approved availability. "
        "Audit-only candidates are timestamp-as-close and timestamp-as-start plus 60 minutes. "
        "The latter is conservative relative to those two candidates, but cannot establish "
        "actual publication latency. Neither is an approved feature join.",
        "",
    ]
    return "\n".join(lines)


def save_course_audit(directory: Path, audit: dict) -> None:
    write_json(directory / "course_manifest.json", audit)
    atomic_new(directory / "course_audit.md", course_markdown(audit).encode())
