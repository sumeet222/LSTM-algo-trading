"""Small immutable table boundaries; no trading, model or market-source imports."""

import csv
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

BASE = Path("trading/track2/final_directional_slate_v1")
RAW = BASE / "runs/sizing-matched-20261110-r1/results"
ROOT = Path("trading/track2/final3_risk_attribution_v1")
CODE = Path("src/lstm_data/trading/track2/final3_risk_attribution")
ARMS = ("EQUAL", "ROLLING_RISK", "EWMA_RISK", "S2C_RISK")
POLICIES = {"F1": "R01-A", "F3": "M04-T480", "F4": "R07-PERSIST"}
NI = "NOT_IDENTIFIABLE_FROM_SAVED_OUTPUTS"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(2**20), b""):
            h.update(b)
    return h.hexdigest()


def canonical(x: object) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def publish(path: Path, x: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        f.write(json.dumps(x, sort_keys=True, indent=2, default=str) + "\n")


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    names = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("x", newline="") as f:
        w = csv.DictWriter(f, fieldnames=names)
        w.writeheader()
        w.writerows(rows)


def table(value: object) -> pd.DataFrame:
    if not isinstance(value, pd.DataFrame):
        raise ValueError("EXPECTED_DATAFRAME")
    return value


def col(frame: pd.DataFrame, name: str) -> pd.Series:
    v = frame[name]
    if not isinstance(v, pd.Series):
        raise ValueError("AMBIGUOUS_COLUMN " + name)
    return v


def records(frame: pd.DataFrame) -> list[SimpleNamespace]:
    return [SimpleNamespace(**{str(k): v for k, v in r.items()}) for r in frame.to_dict("records")]


def prepare() -> None:
    """Hash relevant settled inputs before any new artifact write."""
    if ROOT.exists():
        raise FileExistsError("USE_NEW_VERSION_OR_EXISTING_READ_ONLY_RESULTS")
    manifest = load(BASE / "FINAL_SLATE_CONTENT_MANIFEST.json")
    role = {
        "analysis_03/COMBINED_DAILY_NAV.parquet": "canonical daily accounts",
        "analysis_03/ANALYSIS_MANIFEST.json": "canonical derived validation",
        "FOUR_ARM_S2C_SIZING_RESULTS.csv": "canonical final financial anchors",
        "FIVE_ALGORITHM_REGISTRY.json": "frozen alpha/cost/selection protocol",
        "REGISTRY_SEAL.json": "five-policy seal",
        "OVERLAY_RUN_REGISTRY.json": "actual overlay code/source/selection identity",
        "SELECTION_RECEIPT.json": "frozen three-family selection",
        "S2C_MATCHED_VS_ATTAINABLE.csv": "causal opportunity/readiness denominators",
        "FIXED_POLICY_RISK_CAUSE_SUPPORT.csv": "fixed partial-risk attribution caveat",
        "EXPORT_SCHEMA_AND_COUNTING.md": "book arm/sample schema convention",
        "VALIDATION_AND_REPRODUCE.md": "source/validation interpretation",
        "FINAL_DIRECTIONAL_AND_SIZING_HANDOFF.md": "human handoff",
        "analysis_03/PAIRED_FUNDED_PATH_DIVERGENCE.csv": "prior executed-key join witness",
        "analysis_03/CONCENTRATION_AND_TAILS.csv": "prior concentration check",
        "analysis_03/ANNUAL_NAV_AND_COSTS.csv": "prior calendar-year monetary check",
        "runs/sizing-matched-20261110-r1/RUN_RECEIPT.json": "matched run frontier",
        "runs/sizing-matched-20261110-r1/results/OUTPUT_MANIFEST.json": (
            "settled result file hashes"
        ),
        "runs/sizing-matched-20261110-r1/results/RESULTS.csv": "original Decimal financial amounts",
        "runs/sizing-matched-20261110-r1/results/DAILY_NAV.parquet": (
            "independent daily export crosscheck"
        ),
        "runs/sizing-matched-20261110-r1/results/COHORTS.parquet": (
            "complete closed-cohort allocations"
        ),
        "runs/sizing-matched-20261110-r1/results/PHYSICAL_FILLS.parquet": (
            "external fills and costs"
        ),
        "runs/sizing-matched-20261110-r1/results/EXIT_REASONS.csv": "dynamic grouped exit counters",
        "runs/sizing-matched-20261110-r1/results/ATTRIBUTION.csv": (
            "source aggregate/rejection counters"
        ),
    }
    registry = []
    import pyarrow.parquet as pq

    for name, purpose in role.items():
        p = BASE / name
        h = digest(p)
        expected = manifest["files"][str(p)]["sha256"]
        if h != expected:
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION " + str(p))
        n = (
            pq.read_metadata(p).num_rows
            if p.suffix == ".parquet"
            else (len(csv_rows(p)) if p.suffix == ".csv" else None)
        )
        registry.append(
            {
                "path": str(p),
                "sha256": h,
                "mtime_ns": p.stat().st_mtime_ns,
                "bytes": p.stat().st_size,
                "role": purpose,
                "row_count": n,
                "policies": list(POLICIES.values()),
                "arms": ARMS,
                "population": "MATCHED_PRIMARY; other rows present only in named mixed containers",
                "period": ["2021-01-04", "2024-12-31"],
            }
        )
    for p, purpose in [
        (BASE / "FINAL_SLATE_CONTENT_MANIFEST.json", "final root content anchor"),
        (Path("trading/track2/stage012/original_bundles.json"), "original model path/hash anchor"),
        (
            Path("trading/track2/stage012/SOURCE_AND_MODEL_REGISTRY.md"),
            "original model architecture anchor",
        ),
    ]:
        registry.append(
            {
                "path": str(p),
                "sha256": digest(p),
                "mtime_ns": p.stat().st_mtime_ns,
                "bytes": p.stat().st_size,
                "role": purpose,
                "row_count": None,
            }
        )
    ROOT.mkdir(exist_ok=False)
    publish(
        ROOT / "SOURCE_REGISTER_BEFORE.json",
        {"files": registry, "scope": "Relevant inputs only; no raw source/model/checkpoint read"},
    )
    protocol = {
        "scope": "READ_ONLY_SAVED_PORTFOLIO_RISK_1",
        "population": "MATCHED_ONLY_PRIMARY",
        "policy_ids": POLICIES,
        "arms": ARMS,
        "expected_accounts": 12,
        "sessions": 1005,
        "initial_NAV": 100000,
        "USD_tolerance": "1e-7",
        "CAGR": "actual first-last calendar days/365.25",
        "daily_returns": "NAV_t/NAV_previous-1; initial100000",
        "annualization": 252,
        "SD_ddof": 1,
        "Sortino": "sqrt252*mean/sqrt(mean(min(r,0)^2)), all sessions",
        "VaR": "negative linear return quantile at .05/.01; positive means loss",
        "ES": "negative mean of worst ceil(alpha*N) returns; stable date order breaks ties",
        "drawdown": (
            "initial NAV included, recovery>=prior peak, underwater counts dd<0 observations"
        ),
        "exposure_bins": [0, 0.05, 0.10, 0.20, 0.40, 1.0, "infinity"],
        "zero_exposure_threshold": 1e-12,
        "normalization": (
            "both constant control/S2C realized mean RTH gross and realized annual vol ratios"
        ),
        "minimum_mean_gross_for_scaling": 1e-6,
        "minimum_vol_for_scaling": 1e-12,
        "maximum_proxy_scale": 10,
        "scaled_return_nonpositive_wealth": "REFUSE",
        "scaled_proxy": "NONEXECUTABLE; multiply already-net daily returns; no orders or new fees",
        "paired_tails": "control worst/best ceil(.05*N) and worst ceil(.01*N), same dates for S2C",
        "bootstrap": (
            "NOT_RUN_OPTIONAL; paired48 monthly/four annual deltas; inference deferred Stage6"
        ),
        "channel_rubric": (
            "No composite. Full-period + all annual nonnegative = "
            "SUPPORTED_EXPLORATORY; conflicting = MIXED; nonpositive with no "
            "consistent gain = NO_EVIDENCE; absent = NOT_IDENTIFIABLE"
        ),
        "low_support_descriptive_strata": 20,
        "future_prices_neural_trading_replays": 0,
        "output_soft_bytes": 10_000_000,
        "hard_bytes": 50_000_000,
    }
    protocol["identity"] = canonical(protocol)
    publish(ROOT / "ANALYSIS_PROTOCOL.json", protocol)


def verify_inputs() -> None:
    for r in load(ROOT / "SOURCE_REGISTER_BEFORE.json")["files"]:
        p = Path(r["path"])
        if digest(p) != r["sha256"] or p.stat().st_mtime_ns != r["mtime_ns"]:
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION " + str(p))
