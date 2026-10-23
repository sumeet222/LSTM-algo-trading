"""Offline P019 source-isolated identity checks and deterministic jump inventory.

This module cannot build features, labels, transforms, or fits. All numerical
reads require an exact active 018D manifest member and verified physical bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.p2_closure import load_deferred_work

REVISION = "776328445b7ac6e7815ef3a483e9c8ded1eb6d56"
SYMBOLS = tuple(
    "VZ COP BAC BA AAPL PEP MRK SBUX CVX MS AMD KO JNJ AMZN XOM WFC AVGO TSLA MA CSCO".split()
)
MANIFEST_SHA = "2b8f9165b0387acaf650d1f1514afb8b41d081aacc9b2056b2f6efa496adf40c"


def digest(path: Path) -> str:
    """Hash bytes without loading the file into memory."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path: Path, value: object) -> None:
    """Publish a new artifact; never replace a prior audit output."""
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, default=str)
        stream.write("\n")


class ActivePanel:
    """Exact manifest-bound paths; no discovery or fallback to another source."""

    def __init__(self, root: Path, config: dict) -> None:
        self.root = root.resolve()
        self.config = config
        if (
            config["revision"] != REVISION
            or tuple(config["symbols"]) != SYMBOLS
            or config["manifest_sha256"] != MANIFEST_SHA
        ):
            raise ValueError("STOP_IDENTITY: configuration changed")
        manifest_path = self.root / config["manifest"]
        if digest(manifest_path) != MANIFEST_SHA:
            raise ValueError("STOP_IDENTITY: manifest bytes changed")
        self.manifest = json.loads(manifest_path.read_text())
        if (
            self.manifest["revision"] != REVISION
            or self.manifest["dataset"] != "mito0o852/OHLCV-1m"
            or self.manifest["namespace"] != "HF20_HF1M_LONG_v1"
        ):
            raise ValueError("STOP_IDENTITY: wrong source")
        self.months = self.manifest["monthly"]
        expected = pd.period_range("2010-07", "2026-03", freq="M").astype(str).tolist()
        if [m["month"] for m in self.months] != expected:
            raise ValueError("STOP_IDENTITY: active month order")
        self.refs: dict[str, dict] = {}
        for month in self.months:
            key = month["month"]
            raw = {
                "path": month["raw_path"],
                "bytes": month["raw_bytes"],
                "sha256": month["raw_sha256"],
            }
            expected_raw = f"data/raw/hf20_hf1m_long_v1/{REVISION}/raw_1m_selected/{key}.parquet"
            if key == "2026-03":
                expected_raw = (
                    f"data/raw/hf20_hf1m_15y_v1/{REVISION}/"
                    "raw_selected_1m/year=2026/month=03/selected.parquet"
                )
            if raw["path"] != expected_raw:
                raise ValueError("STOP_IDENTITY: raw path")
            self.refs[raw["path"]] = raw
            for kind, ref in month["derived_files"].items():
                allowed = f"data/processed/hf20_hf1m_long_v1/{REVISION}/qa_v2/{kind}/{key}.parquet"
                if ref["path"] != allowed:
                    raise ValueError("STOP_IDENTITY: derived path")
                self.refs[ref["path"]] = ref
        self.verified: set[str] = set()

    def verify_all(self) -> list[dict]:
        """Verify all 1,701 active raw/derived files, without opening legacy roots."""
        receipts = []
        for name, ref in self.refs.items():
            path = (self.root / name).resolve()
            if not path.is_relative_to(self.root):
                raise ValueError("STOP_IDENTITY: path escape")
            if path.stat().st_size != ref["bytes"] or digest(path) != ref["sha256"]:
                raise ValueError(f"STOP_IDENTITY: numerical bytes changed: {name}")
            self.verified.add(name)
            receipts.append(ref)
        return receipts

    def read(self, name: str, columns: list[str] | None = None) -> pd.DataFrame:
        """Reject all nonmembers, including old source and out-of-scope months."""
        if name not in self.refs or name not in self.verified:
            raise ValueError("STOP_IDENTITY: unverified or unallowlisted input")
        return pd.read_parquet(self.root / name, columns=columns)


def scan_stock(
    frame: pd.DataFrame, prior: dict[str, pd.DataFrame], threshold: float, range_threshold: float
) -> list[dict]:
    """Flag genuine discontinuities, retaining earlier endpoints across months.

    `prior` is scan-only state, never causal input state. Session medians use
    retrospective data solely to propose events for external investigation.
    """
    found: dict[str, dict] = {}

    def add(row: pd.Series, before: pd.Series | None, rule: str) -> None:
        key = str(row.timestamp)
        if key not in found:
            record = {f"after_{k}": v for k, v in row.to_dict().items()}
            record.update(
                {f"before_{k}": v for k, v in before.to_dict().items()}
                if before is not None
                else {}
            )
            record["rules"] = []
            found[key] = record
        found[key]["rules"].append(rule)

    frame = frame.sort_values("timestamp").reset_index(drop=True)
    for stream, selected in (("ALL_SESSION", frame), ("RTH", frame.loc[frame.is_rth])):
        old = prior.get(stream, selected.iloc[:0])
        combined = pd.concat([old, selected], ignore_index=True)
        closes = combined.close.to_numpy(dtype=float)
        opens = combined.open.to_numpy(dtype=float)
        if len(combined) > 1:
            changes = np.abs(np.log(closes[1:] / closes[:-1])) > np.log(threshold)
            open_breaks = np.abs(np.log(opens[1:] / closes[:-1])) > np.log(threshold)
            hits = np.flatnonzero(changes | (open_breaks if stream == "ALL_SESSION" else False)) + 1
            for index in hits:
                if index < len(old):
                    continue
                if changes[index - 1]:
                    add(combined.iloc[index], combined.iloc[index - 1], stream + "_ADJACENT_CLOSE")
                if stream == "ALL_SESSION" and open_breaks[index - 1]:
                    add(combined.iloc[index], combined.iloc[index - 1], "ALL_SESSION_OPEN_BREAK")
        if len(combined):
            prior[stream] = combined.tail(1)
    body = np.abs(np.log(frame.close.to_numpy() / frame.open.to_numpy())) > np.log(threshold)
    ranges = frame.high.to_numpy() / frame.low.to_numpy() > range_threshold
    for index in np.flatnonzero(body | ranges):
        before = frame.iloc[index - 1] if index else None
        if body[index]:
            add(frame.iloc[index], before, "MINUTE_BODY")
        if ranges[index]:
            add(frame.iloc[index], before, "MINUTE_RANGE")
    rth = frame.loc[frame.is_rth].copy()
    # Strip timezone only from the grouping key after converting to ET. Source
    # UTC instants remain unchanged; this avoids per-row timezone formatting.
    rth["date_et"] = (
        rth.timestamp.dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
    )
    previous_session = prior.get("SESSION")
    for _, session in rth.groupby("date_et", sort=True):
        if previous_session is not None:
            ratio = session.close.head(30).median() / previous_session.close.tail(30).median()
            if abs(np.log(ratio)) > np.log(threshold):
                add(session.iloc[0], previous_session.iloc[-1], "SESSION_MEDIAN_SHIFT")
                found[str(session.iloc[0].timestamp)]["session_median_ratio"] = float(ratio)
        previous_session = session.tail(30)
    if previous_session is not None:
        prior["SESSION"] = previous_session
    return list(found.values())


def run(config_path: Path, out: Path) -> None:
    """Verify identity first, then scan exclusively active canonical observations."""
    started = time.monotonic()
    root = config_path.resolve().parent.parent
    config = json.loads(config_path.read_text())
    out.mkdir(parents=True, exist_ok=False)
    entries = load_deferred_work(root / "configs/track_a_p2_engineering_handoff_v1.json")
    panel = ActivePanel(root, config)
    receipts = panel.verify_all()
    previous = Path(config["manifest"]).parent
    identity = json.loads((root / previous / "identity_initial.json").read_text())
    scope = json.loads((root / previous / "active_scope.json").read_text())
    if tuple(identity["symbols"]) != SYMBOLS or scope["start_date"] != "2010-07-01":
        raise ValueError("STOP_IDENTITY: identity/scope")
    write_json(out / "active_input_hash_receipt.json", receipts)
    write_json(out / "scan_policy_sealed_before_outcomes.json", config)
    text = f"""# P019 dataset identity preflight — PASS_IDENTITY

Source: mito0o852/OHLCV-1m. Revision: {REVISION}.
Namespace: HF20_HF1M_LONG_v1. Active scope: 2010-07-01 through 2026-03-31.
UTC nanosecond minute-start convention; exchange-calendar RTH flags; ET uses America/New_York.
Canonical ordered universe: {", ".join(SYMBOLS)}.
All {len(receipts)} active raw/QA files physically SHA256/size verified against
018D manifest {MANIFEST_SHA}; only its exact paths can be read. March2026 is the
explicit allowlisted 018C cache reuse, not a general fallback. No legacy root scan.
P2 deferred register hash validation passed ({len(entries)} entries); no scientific gates cleared.
Permission: HUMAN_REPORTED_MAINTAINER_PERMISSION_FOR_PRIVATE_RESEARCH; independently unverified;
price-bearing artifacts stay local/ignored; no redistribution authority.
No acquisition, features, targets, scaler fitting, training or held-out model evaluation.
Reserved future namespaces only: HF1M_FT2_v1, HF1M_TG20_v1, HF1M_LONG_TM0.
No downstream store is created before action PASS and readiness GO.
"""
    (out / "P019_DATASET_IDENTITY_PREFLIGHT.md").write_text(text)
    print(text, flush=True)
    states: dict[str, dict[str, pd.DataFrame]] = {s: {} for s in SYMBOLS}
    events = []
    originals = []
    census = []
    for month in panel.months:
        refs = month["derived_files"]
        frame = panel.read(refs["canonical_observed"]["path"])
        # Upstream partitions use exchange months; late ET extended hours can
        # fall on the following UTC date. Stored timestamps remain UTC starts.
        lower = pd.Timestamp(month["month"] + "-01", tz="America/New_York")
        upper = lower + pd.offsets.MonthBegin(1)
        if (
            not set(frame.ticker).issubset(SYMBOLS)
            or not frame.source_revision.eq(REVISION).all()
            or not frame.is_genuine.all()
            or frame.is_imputed.any()
            or not (frame.timestamp.ge(lower) & frame.timestamp.lt(upper)).all()
        ):
            raise ValueError("STOP_IDENTITY: canonical content identity")
        for symbol in SYMBOLS:
            stock = frame.loc[frame.ticker == symbol].copy()
            census.append(
                {
                    "month": month["month"],
                    "ticker": symbol,
                    "rows": len(stock),
                    "rth_rows": int(stock.is_rth.sum()),
                }
            )
            for event in scan_stock(
                stock,
                states[symbol],
                config["symmetric_ratio_threshold"],
                config["intraminute_high_low_threshold"],
            ):
                event["source_month"] = month["month"]
                event["canonical_path"] = refs["canonical_observed"]["path"]
                events.append(event)
        issues = panel.read(refs["minute_quality_issues"]["path"])
        originals.extend(
            issues.loc[issues.issue_type == "ACTION_OR_SCALE_JUMP_OVER25PCT"].to_dict("records")
        )
        print(
            f"{month['month']}: scanned {len(frame)} rows; {len(events)} candidate minutes",
            flush=True,
        )
    inventory = pd.DataFrame(events)
    inventory["event_id"] = [f"P019-{i:03d}" for i in range(1, len(inventory) + 1)]
    inventory["timestamp_et"] = pd.to_datetime(inventory.after_timestamp, utc=True).dt.tz_convert(
        "America/New_York"
    )
    inventory["close_ratio"] = inventory.after_close / inventory.before_close
    inventory["open_ratio"] = inventory.after_open / inventory.before_close
    inventory["elapsed_minutes"] = (
        inventory.after_timestamp - inventory.before_timestamp
    ).dt.total_seconds() / 60
    original_keys = {(r["ticker"], r["timestamp_utc"]) for r in originals}
    inventory["original_018d"] = [
        (r.after_ticker, r.after_timestamp) in original_keys for r in inventory.itertuples()
    ]
    if len(originals) != 13 or inventory.original_018d.sum() != 13:
        raise ValueError("STOP_IDENTITY: original13 not exactly recovered")
    # Prices are never placed in the shareable report tree.
    private = root / "data/processed/hf1m_p019_action_audit_v1" / out.name
    private.mkdir(parents=True, exist_ok=False)
    inventory.to_parquet(private / "event_inventory.parquet", index=False)
    pd.DataFrame(originals).to_parquet(private / "original_018d_13.parquet", index=False)
    pd.DataFrame(census).to_csv(out / "scan_stock_month_census.csv", index=False)
    compact = inventory[
        [
            "event_id",
            "after_ticker",
            "after_timestamp",
            "timestamp_et",
            "rules",
            "close_ratio",
            "open_ratio",
            "elapsed_minutes",
            "original_018d",
            "after_is_rth",
            "before_is_rth",
            "canonical_path",
            "after_source_row",
        ]
    ]
    compact.to_csv(out / "candidate_inventory.csv", index=False)
    write_json(
        out / "scan_receipt.json",
        {
            "rows": sum(r["rows"] for r in census),
            "events": len(inventory),
            "original13": 13,
            "all20_stock_months": len(census),
            "elapsed_seconds": time.monotonic() - started,
            "private_inventory": str(private.relative_to(root)),
            "inventory_sha256": digest(private / "event_inventory.parquet"),
            "policy_sha256": digest(out / "scan_policy_sealed_before_outcomes.json"),
            "status": "EXTERNAL_EVENT_VERIFICATION_PENDING; NO_ACTION_PASS",
        },
    )


def main() -> None:
    """CLI intentionally provides only identity plus read-only source scanning."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=Path("configs/hf1m_p019_action_scan_v1.json")
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.config, args.out)


if __name__ == "__main__":
    main()
