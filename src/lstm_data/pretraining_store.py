"""One compact hash-verified component store and lazy candidate review loader."""
from __future__ import annotations

import gzip
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .config import atomic_new, digest
from .ft0_transforms import identity
from .labels import FitWindow
from .pretraining_policy import CANDIDATE, PreparationAuthority, load_authority, verify_ref
from .pretraining_source import BARRIER, FIRST, LAST
from .pretraining_tables import BaseTables, CanonicalHistory, M2Moments, ProxyPanel
from .pretraining_transforms import (
    CandidateFloors,
    CandidatePreparation,
    CandidateScaler,
    CandidateView,
)
from .stock_features import Components
from .stock_source import StockCalendar, StockDaily


def code_identity(root: Path) -> str:
    """Bind all maintained pipeline code, rather than an untracked notebook state."""
    return identity({str(p.relative_to(root)): digest(p)
                     for p in sorted((root / "src/lstm_data").glob("*.py"))})


def serial(value: object) -> object:
    return json.loads(json.dumps(value, default=str, sort_keys=True))


def save_tables(base: BaseTables, path: Path) -> dict:
    base.history.authority.ensure("FEATURE_TARGET_PREPARATION")
    payload = {
        "schema_version": 1, "universe": CANDIDATE,
        "authority_binding": base.history.authority.binding,
        "source_binding": base.history.binding, "action_binding": base.history.action_binding,
        "components": [asdict(r) for _, r in sorted(base.components.items())],
        "panels": [asdict(r) for _, r in sorted(base.panels.items())],
        "m2": [asdict(r) for _, r in sorted(base.m2.items())],
        "daily_volumes": [{"symbol": s, "session": day, "end": str(r.end), "volume": r.volume,
                           "source_ids": r.source_ids, "share_basis": r.share_basis}
                          for (s, day), r in sorted(base.history.daily.items())],
        "origin_steps": [{"session": day, "origin": o, "positions": positions}
                         for (day, o), positions in sorted(base.origin_steps.items())],
        "designation": "ASSUMPTION_CONDITIONAL_CANDIDATE_NOT_FOR_TRAINING",
    }
    data = json.dumps(payload, default=str, sort_keys=True, separators=(",", ":")).encode()
    atomic_new(path, gzip.compress(data, mtime=0))
    return {"path": str(path.relative_to(base.history.authority.root)), "sha256": digest(path),
            "bytes": path.stat().st_size, "uncompressed_bytes": len(data)}


def load_tables(authority: PreparationAuthority, ref: dict) -> BaseTables:
    """Hash before numerical parsing; no raw archive reread or confirmation features."""
    authority.ensure("FEATURE_TARGET_PREPARATION")
    path = verify_ref(authority.root, ref)
    obj = json.loads(gzip.decompress(path.read_bytes()))
    if (obj.get("schema_version") != 1 or tuple(obj.get("universe", ())) != CANDIDATE
            or obj.get("authority_binding") != authority.binding
            or obj.get("designation") != "ASSUMPTION_CONDITIONAL_CANDIDATE_NOT_FOR_TRAINING"):
        raise ValueError("CANONICAL_CANDIDATE_STORE_IDENTITY_MISMATCH")
    calendar = StockCalendar(FIRST, LAST)
    components = {}
    for r in obj["components"]:
        key = r["symbol"], r["step"]["session"], r["step"]["slot"]
        if key[0] not in CANDIDATE or key in components:
            raise ValueError("DUPLICATE_OR_UNKNOWN_COMPONENT_KEY")
        step = calendar.steps[calendar._positions[key[1], key[2]]]
        if step.end >= BARRIER or r["step"]["end"] != str(step.end):
            raise ValueError("CONFIRMATION_OR_COMPONENT_CLOCK_MISMATCH")
        components[key] = Components(r["symbol"], step, r["values"], r["coverage"],
                                     r["source_binding"], r["action_binding"],
                                     tuple(r["source_ids"]), r["source_only"],
                                     tuple(r["flags"]), r["lineage_id"])
    panels = {}
    for saved in obj["panels"]:
        r = dict(saved)
        for name in ("cutoff", "issuance", "entry_event", "exit_event", "maturity"):
            r[name] = pd.Timestamp(r[name]) if r[name] is not None else None
        if r["cutoff"] >= BARRIER or r["exit_event"] >= BARRIER:
            raise ValueError("CONFIRMATION_TARGET_STORE_FORBIDDEN")
        for name in ("entry_prices", "exit_prices", "entry_valid", "outcome_valid", "returns"):
            r[name] = tuple(r[name])
        r["reference_ids"] = tuple(tuple(x) for x in r["reference_ids"])
        panel = ProxyPanel(**r)
        if (panel.session, panel.origin) in panels:
            raise ValueError("DUPLICATE_PROXY_PANEL")
        panels[panel.session, panel.origin] = panel
    moments = {}
    for saved in obj["m2"]:
        r = dict(saved)
        r["maturity"] = pd.Timestamp(r["maturity"]) if r["maturity"] is not None else None
        stat = M2Moments(**r)
        key = stat.symbol, stat.session, stat.origin
        if key in moments:
            raise ValueError("DUPLICATE_M2_MOMENTS")
        moments[key] = stat
    daily = {}
    for r in obj["daily_volumes"]:
        row = StockDaily(r["symbol"], r["session"], pd.Timestamp(r["end"]), None, r["volume"],
                         None, None, None, tuple(r["source_ids"]), None, None, "ASSUMED", False,
                         r["share_basis"], universe=CANDIDATE)
        if row.end >= BARRIER:
            raise ValueError("CONFIRMATION_DAILY_STORE_FORBIDDEN")
        daily[row.symbol, row.session] = row
    history = CanonicalHistory(calendar, daily, authority, obj["source_binding"],
                               obj["action_binding"])
    windows = {(r["session"], r["origin"]): tuple(r["positions"]) for r in obj["origin_steps"]}
    return BaseTables(history, components, panels, moments, windows)


def save_preparation(preparation: CandidatePreparation, path: Path) -> dict:
    value = serial(asdict(preparation))
    atomic_new(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
    return {"path": str(path), "sha256": digest(path),
            "preparation_id": preparation.preparation_id}


def read_preparation(root: Path, ref: dict) -> CandidatePreparation:
    obj = json.loads(verify_ref(root, ref).read_text())
    w = obj["window"]
    window = FitWindow(w["window_id"], pd.Timestamp(w["start"]), pd.Timestamp(w["stop"]),
                       pd.Timestamp(w["fitted_at"]), w["phase"])
    scaler = obj["scaler"]
    prep = CandidatePreparation(
        window, tuple(CandidateFloors(**r) for r in obj["floors"]),
        CandidateScaler(tuple(scaler["centers"]), tuple(scaler["scales"]),
                        tuple(scaler["methods"])), obj["target_epsilon"],
        obj["authority_binding"], obj["source_binding"], obj["action_binding"],
        obj["population_binding"], obj["population_counts"], obj["constructed_at"],
        obj["designation"],
    )
    if prep.preparation_id != ref["preparation_id"]:
        raise ValueError("PREPARATION_NUMERIC_IDENTITY_CHANGED")
    return prep


def load_candidate_view(root: Path, manifest_ref: dict, preparation_key: str) -> CandidateView:
    """Safe review loader. Its return value cannot be passed as real FitData/NeuralView."""
    manifest = json.loads(verify_ref(root, manifest_ref).read_text())
    if (manifest.get("MODEL_FIT_FORBIDDEN") is not True
            or manifest.get("production_migrated") is not False
            or manifest.get("code_sha256") != code_identity(root)):
        raise ValueError("CANDIDATE_CODE_SCOPE_OR_CACHE_MISMATCH")
    binding = manifest["authority"]
    authority = load_authority(root, binding["policy_ref"], binding["approval_ref"])
    base = load_tables(authority, manifest["canonical_store"])
    preparation = read_preparation(root, manifest["preparations"][preparation_key])
    return CandidateView(base, preparation)
