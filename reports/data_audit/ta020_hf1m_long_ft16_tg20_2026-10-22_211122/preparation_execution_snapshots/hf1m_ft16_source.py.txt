"""P020 exact source allowlists and protected-period numeric read barrier."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .hf1m_action_audit import REVISION, SYMBOLS, digest
from .hf1m_action_source import NAMESPACE

CONFIG = Path("configs/hf1m_long_ft16_v1.json")
BARRIER = "2026-01-01"
ORDER = tuple("M1 M2 M3 M4 V1 V2 V3 B1 B2 Q1 Q2 T1 T2 T3 T4 T5".split())
COMMON = tuple(x for x in ORDER if x != "M2")
BOUNDED = {"B2", "T2", "T5"}


def ref(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}


def checked(ref_: dict) -> Path:
    path = Path(ref_["path"])
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("STOP_IDENTITY: nonportable input")
    if digest(path) != ref_["sha256"] or path.stat().st_size != ref_["bytes"]:
        raise ValueError("STOP_IDENTITY: input bytes changed")
    return path


def configuration(path: Path = CONFIG) -> dict:
    c = json.loads(path.read_text())
    if (
        c["revision"] != REVISION
        or tuple(c["symbols"]) != SYMBOLS
        or c["parent_namespace"] != NAMESPACE
        or tuple(c["feature_order"]) != ORDER
        or c["protected"][0] != BARRIER
        or c["development"][1] != "2025-12-31"
        or c["feature_id"] != "HF20_HF1M_LONG_v1_FT16_v1"
        or c["target_id"] != "HF20_HF1M_LONG_v1_TG20_4H_v1"
    ):
        raise ValueError("STOP_IDENTITY: wrong P020 identity")
    return c


def verify_parent(c: dict) -> dict:
    """Verify every parent hash; protected Parquet bytes may be hashed, never decoded."""
    up = Path(c["upstream_packet"])
    if digest(up / "pre_feature_gate.json") != c["upstream_gate_sha256"]:
        raise ValueError("STOP_IDENTITY: stale release")
    g = json.loads((up / "pre_feature_gate.json").read_text())
    if (
        g["status"] != "PRE_FEATURE_READY_WITH_QUARANTINES"
        or g["uncontrolled_candidates"] != 0
        or digest(Path(g["root_register"]["path"])) != c["root_register_sha256"]
    ):
        raise ValueError("STOP_IDENTITY: action/root release")
    for name, sha in g["evidence_sha256"].items():
        if digest(up / name) != sha:
            raise ValueError("STOP_IDENTITY: parent binding")
    pointer = json.loads((up / "canonical_event_ledger_pointer.json").read_text())
    if pointer["path"] != "unresolved_event_ledger_v3.json":
        raise ValueError("STOP_IDENTITY: stale action ledger")
    m = json.loads((up / "adjusted_hourly_manifest.json").read_text())
    expected = Path("data/processed/hf20_hf1m_long_v1_action_qa_v1") / up.name
    if m["namespace"] != NAMESPACE or Path(m["private_root"]) != expected:
        raise ValueError("STOP_IDENTITY: source mixing")
    for record in m["monthly"]:
        r = record["files"]["hourly"]
        if Path(r["path"]) != expected / "hourly" / (record["month"] + ".parquet"):
            raise ValueError("STOP_IDENTITY: hourly path")
        checked(r)
    for name, key in [("hour_field_mask_manifest.json", "file")]:
        checked(json.loads((up / name).read_text())[key])
    a = json.loads((up / "candidate_origin_summary_v2.json").read_text())
    for r in a["files"].values():
        checked(r)
    return m


def read_hourly(c: dict, stop: str = "2025-12-31") -> pd.DataFrame:
    """No broad date query: protected monthly price partitions are never opened."""
    if stop >= BARRIER or stop < "2010-07-01":
        raise ValueError("P020_PROTECTED_NUMERIC_ACCESS_DENIED")
    manifest = verify_parent(c)
    frames = []
    for row in manifest["monthly"]:
        if row["month"] > stop[:7]:
            continue
        frame = pd.read_parquet(checked(row["files"]["hourly"]))
        frame = frame.loc[frame.session_date_et.le(stop)].copy()
        if frame.session_date_et.ge(BARRIER).any() or not frame.is_rth.all():
            raise ValueError("P020_PROTECTED_OR_EH_ACCESS")
        frames.append(frame)
    result = pd.concat(frames, ignore_index=True)
    if set(result.ticker) != set(SYMBOLS) or result.source_revision.ne(REVISION).any():
        raise ValueError("STOP_IDENTITY: rows/order")
    return result


def source_masks(c: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Source-quality booleans and calendar keys only; no price/target values."""
    up = Path(c["upstream_packet"])
    a = json.loads((up / "candidate_origin_summary_v2.json").read_text())
    mask = pd.read_parquet(checked(a["files"]["stock_origin_masks"]))
    clock = pd.read_parquet(checked(a["files"]["origin_clock"]))
    return mask, clock
