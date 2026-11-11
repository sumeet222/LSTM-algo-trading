"""Immutable identities and deterministic predeclared selection contract."""

import json
from pathlib import Path

from ..rapid_final_diag.provenance import inventory as prior_inventory
from ..rapid_v1.paths import canonical, digest, publish
from ..rapid_v1.verification import preserve_check

ROOT = Path("trading/track2/final_directional_slate_v1")
CODE = Path("src/lstm_data/trading/track2/final_directional_slate")
FINAL = Path("trading/track2/rapid_final_diag_v1")
FINAL_RUN = FINAL / "runs/final-diag-20261110-r1/funded"
V2 = Path(
    "trading/track2/rapid_v2_diagnostics/runs/rapid-v2-20261110-r1/results_20261110T225245268428Z"
)
CACHE = Path("trading/track2/stage35/completion_v2/audits/cache")
RISK = Path(
    "trading/track2/stage012/audits/completion_v1/historical_run_v1/RISK_REFERENCE_MANIFEST.json"
)
COVERAGE = Path("trading/track2/stage35/completion_v2/FULL_SIGNAL_COVERAGE_REPORT.json")
BUNDLES = Path("trading/track2/stage012/original_bundles.json")
POLICIES = {
    "F1": {
        "label": "R01-A",
        "strategy": "R01",
        "family": "R01",
        "headroom": ".85",
        "source": str(FINAL_RUN),
        "case": "R01_CONTROL",
        "engine": "V3_DYNAMIC",
        "change": "NONE",
        "horizon": 10,
        "unit": "max_sessions",
    },
    "F2": {
        "label": "R01-B",
        "strategy": "R01",
        "family": "R01",
        "headroom": "1",
        "source": str(FINAL_RUN),
        "case": "R01_V20",
        "engine": "V3_DYNAMIC",
        "change": "EXACT_V20_ENTRY_RESERVE",
        "horizon": 10,
        "unit": "max_sessions",
    },
    "F3": {
        "label": "M04-T480",
        "strategy": "M04",
        "family": "M04",
        "headroom": "1",
        "source": str(V2),
        "case": "M04_T480",
        "engine": "V2_FIXED",
        "change": "NONE",
        "horizon": 480,
        "unit": "minutes",
    },
    "F4": {
        "label": "R07-PERSIST",
        "strategy": "R07",
        "family": "R07",
        "headroom": ".85",
        "source": str(FINAL_RUN),
        "case": "R07_DAILY2",
        "engine": "V3_DYNAMIC",
        "change": "TWO_DISTINCT_DAILY_EVENT_CHECKS",
        "horizon": 10,
        "unit": "max_sessions",
    },
    "F5": {
        "label": "M05-PERSIST",
        "strategy": "M05",
        "family": "M05",
        "headroom": ".85",
        "source": str(FINAL_RUN),
        "case": "M05_EVENT2",
        "engine": "V3_DYNAMIC",
        "change": "TWO_DISTINCT_VALID_EVENT_CHECKS",
        "horizon": 780,
        "unit": "max_scheduled_minutes",
    },
}
WEIGHTS = {
    "net_PnL_USD": 0.30,
    "net_per_1M_RTH_gross_dollar_years_USD": 0.25,
    "positive_years": 0.15,
    "drawdown_score": 0.15,
    "net_without_top_two": 0.10,
    "cost_margin": 0.05,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def seal_inputs() -> None:
    paths = prior_inventory()
    manifest = FINAL / "FINAL_DIAGNOSTIC_CONTENT_MANIFEST.json"
    for name, item in load(manifest)["files"].items():
        p = Path(name)
        if digest(p) != item["sha256"]:
            raise ValueError("FINAL_ARCHIVE_DRIFT " + name)
        paths[name] = {
            "sha256": digest(p),
            "mtime_ns": p.stat().st_mtime_ns,
            "bytes": p.stat().st_size,
        }
    paths[str(manifest)] = {
        "sha256": digest(manifest),
        "mtime_ns": manifest.stat().st_mtime_ns,
        "bytes": manifest.stat().st_size,
    }
    # Explicit model identity, without loading or importing a neural network.
    for bundle in load(BUNDLES)["bundles"].values():
        for key, sha in zip(
            ("checkpoint", "recipe", "calibration", "phases"), bundle["sha256"], strict=True
        ):
            p = Path(bundle[key])
            if digest(p) != sha:
                raise ValueError("ORIGINAL_MODEL_IDENTITY " + str(p))
            paths[str(p)] = {
                "sha256": sha,
                "mtime_ns": p.stat().st_mtime_ns,
                "bytes": p.stat().st_size,
            }
    extra = [
        RISK,
        BUNDLES,
        COVERAGE,
        CACHE / "CACHE_READY.json",
        CACHE / "matured_source_moves.npy",
        CACHE / "movement_geometry.parquet",
    ]
    for r in load(COVERAGE)["partitions"]:
        p = Path(r["path"])
        if digest(p) != r["sha256"]:
            raise ValueError("FORECAST_PARTITION_DRIFT")
        extra.append(p)
    for p in extra:
        paths[str(p)] = {
            "sha256": digest(p),
            "mtime_ns": p.stat().st_mtime_ns,
            "bytes": p.stat().st_size,
        }
    publish(ROOT / "INPUTS_BEFORE.json", paths)
    preserve_check(ROOT / "PROTECTED_BEFORE.json")


def verify_inputs() -> None:
    for name, r in load(ROOT / "INPUTS_BEFORE.json").items():
        p = Path(name)
        if digest(p) != r["sha256"] or p.stat().st_mtime_ns != r["mtime_ns"]:
            raise ValueError("INPUT_IDENTITY_HOLD " + name)


def freeze() -> None:
    body = {
        "schema": "HF20_FIVE_USER_FROZEN_1",
        "policies": POLICIES,
        "weights": WEIGHTS,
        "period": ["2021-01-01", "2024-12-31"],
        "initial_USD": 100000,
        "minimum_closed_cohorts": 80,
        "family_limit_R01": 1,
        "selection": "descending weighted within-five percentile; ties middle; then ID",
        "target_families": 3,
        "min_families": 2,
        "unsupported_metric": "RANKING_HOLD",
        "percentile": "(ascending average rank-1)/(n-1); one candidate=.5",
        "drawdown_score": "-abs(max_drawdown)",
        "cost_margin": "(gross_price+actions-total_cost)/total_cost",
        "source_inputs_sha256": digest(ROOT / "INPUTS_BEFORE.json"),
        "instruction_sha256": digest(ROOT / "USER_INSTRUCTION_TRANSCRIPTION.md"),
        "instruction_source": "Current user conversation; normalized operative transcription",
        "spec_sha256": digest(ROOT / "FIVE_ALGORITHM_FROZEN_SPEC.md"),
        "overlay": {
            "arms": ["EQUAL", "ROLLING_RISK", "EWMA_RISK", "S2C_RISK"],
            "formula": "g=clip(b/max(scale,m_floor),.5,1.5)",
            "allocation": "headroom_budget*g_i/sum(g_ready); name cap; no redistribution",
            "classical": "last60 scheduled same-slot strictly matured moves, min40, no missing",
            "ewma": "RMS .94 first-square initialization over exact same window",
            "scope": "ENTRY_ONLY; unchanged direction/exit/cost/risk; no neural inference",
            "readiness": (
                "No sign mask; EQUAL parent only, classical own mature input, S2C original input"
            ),
            "primary": "MATCHED_4ARM",
            "secondary": "ATTAINABLE",
            "attainable_equal": "reuse exact original candidate, no identical full rerun",
            "batch": "12 primary books then <=9 secondary books, shared features/risk cache",
            "null": "NOT_RUN unless existing approved module identified",
            "magnitude_target": "nominal origin to240scheduled-minute absolute log return",
            "horizon_mismatch": "short-term entry-risk proxy, not ten-session variance",
        },
        "acceptance": [
            "all five financial bridges",
            "1005 daily rows/control/source identity",
            "all old hashes/mtimes unchanged",
            "no future selection/control/sign leakage",
            "source-backed g=1 policy parity",
            "partial/fee/action/borrow invariants",
            "four-arm common source counts",
            "zero unpriced material terminal exposure",
            "rank audit published before overlay",
            "output<200MB",
        ],
        "comparison_code": {str(p): digest(p) for p in sorted(CODE.glob("*.py"))},
    }
    body["identity"] = canonical(body)
    publish(ROOT / "FIVE_ALGORITHM_REGISTRY.json", body)
    publish(ROOT / "REGISTRY_SEAL.json", {"sha256": digest(ROOT / "FIVE_ALGORITHM_REGISTRY.json")})
