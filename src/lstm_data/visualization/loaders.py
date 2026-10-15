"""Hash-bound local adapters. Raw Arrow predicates precede numeric deserialization."""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from ..aggregation import aggregate_session_hours
from ..calendar import fully_inside_rth, schedule, session_grid
from ..clocks import execution_plan, session_clock
from ..config import digest
from ..ft0_transforms import ORDER
from ..market_features import MarketMeasures
from ..pretraining_market import conditional_vector
from ..pretraining_policy import CANDIDATE, load_authority, local_path
from ..pretraining_source import BARRIER, COLUMNS, FIRST
from ..pretraining_store import load_tables, read_preparation
from ..pretraining_tables import BaseTables
from ..pretraining_transforms import CandidateView, raw_features
from ..stock_source import numeric
from ..validation import normalize, require_valid

ET = "America/New_York"
PARTITIONS = ("Development", "Inner validation", "Refit training")
CAVEAT = (
    "ASSUMPTION_CONDITIONAL · retrospective five-stock universe/actions · "
    "idealized completed-bar clock · researcher-attested local rights, "
    "uninspected private evidence. "
    "SPY is an ETF proxy; hourly-close labels are not fills. No alpha or gate promotion."
)


class ViewUnavailable(ValueError):
    """A safe, user-readable unavailable or integrity state."""


def date_window(start: str, end: str, maximum_days: int = 93) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Reject protected dates before any file access; dates are inclusive Eastern days."""
    a = pd.Timestamp(start, tz=ET).tz_convert("UTC")
    b = (pd.Timestamp(end, tz=ET) + pd.DateOffset(days=1)).tz_convert("UTC")
    if a < pd.Timestamp(FIRST, tz=ET) or b > BARRIER or a >= b:
        raise ViewUnavailable("Only permitted history through June 30, 2024 is available.")
    if (pd.Timestamp(end) - pd.Timestamp(start)).days > maximum_days:
        raise ViewUnavailable(f"Choose at most {maximum_days + 1} days for an interactive chart.")
    return a, b


def symbol_required(symbol: str) -> None:
    if symbol not in CANDIDATE:
        raise ViewUnavailable("Select one of the five candidate stocks.")


@lru_cache(maxsize=2048)
def _file_digest(path: str, size: int, modified: int, changed: int) -> str:
    # Stat keys invalidate verification caches after replacement or ordinary edits.
    return digest(Path(path))


def verified(root: Path, ref: dict) -> Path:
    path = local_path(root, ref["path"])
    if not path.is_file():
        raise ViewUnavailable(f"Local artifact unavailable: {ref['path']}. See Quickstart setup.")
    st = path.stat()
    if _file_digest(str(path), st.st_size, st.st_mtime_ns, st.st_ctime_ns) != ref["sha256"]:
        raise ViewUnavailable(f"Source provenance unverified: hash changed for {ref['path']}.")
    return path


def read_json(root: Path, ref: dict) -> dict:
    return json.loads(verified(root, ref).read_text())


def read_csv(root: Path, ref: dict) -> pd.DataFrame:
    return pd.read_csv(verified(root, ref), float_precision="round_trip")


@dataclass(frozen=True)
class Catalog:
    """Only read activities, project-confined paths and explicitly bound historical files."""

    root: Path
    config: dict

    @classmethod
    def discover(cls, root: Path) -> Catalog:
        config = json.loads((root / "configs/track_a_visualization_v1.json").read_text())
        if config.get("id") != "TA010_READONLY_LOCAL_VISUALIZATION_v1":
            raise ViewUnavailable("Visualization configuration unavailable or unsupported.")
        for name, sha in config["readers"].items():
            verified(root, {"path": name, "sha256": sha})
        return cls(root.resolve(), config)

    def require(self, activity: str) -> None:
        if activity not in {
            "READ_SOURCE",
            "READ_FEATURES",
            "READ_SAVED_PREDICTIONS",
            "READ_DIAGNOSTICS",
        }:
            raise ViewUnavailable(
                "Visualization is read-only: fits, writes and trading are forbidden."
            )

    def token(self) -> tuple:
        """Invalidate on bound file changes without decoding prices."""
        refs: dict[str, tuple] = {}

        def walk(value: object) -> None:
            if isinstance(value, dict):
                if "path" in value and "sha256" in value:
                    path = local_path(self.root, str(value["path"]))
                    s = path.stat() if path.exists() else None
                    refs[str(value["path"])] = (
                        value["sha256"],
                        s.st_size if s else -1,
                        s.st_mtime_ns if s else -1,
                        s.st_ctime_ns if s else -1,
                    )
                for v in value.values():
                    walk(v)
            elif isinstance(value, list):
                for v in value:
                    walk(v)

        walk(self.config)
        manifest = read_json(self.root, self.config["manifest"])
        walk(manifest)
        source = read_json(self.root, self.config["source_manifest"])
        for refs_for_stock in source["source_by_stock"].values():
            for ref in refs_for_stock:
                walk({"path": ref["data"], "sha256": ref["sha256"]})
                walk({"path": ref["manifest"], "sha256": ref["manifest_sha256"]})
        return tuple(sorted(refs.items()))

    def missing_required(self, token: tuple) -> list[str]:
        """Saved snapshots work without optional weights; name all other missing dependencies."""
        weights = {
            ref["path"]
            for models in self.config.get("checkpoints", {}).values()
            for ref in models.values()
        }
        return [name for name, metadata in token if metadata[1] < 0 and name not in weights]

    def model_names(self, fold: str, partition: str = "Development") -> tuple[str, ...]:
        if fold not in self.config["models"] or partition not in PARTITIONS:
            raise ViewUnavailable(
                "Timeframe unavailable. Choose WF1 or WF2 and a recorded partition."
            )
        neural = tuple(n for n in ("TM0", "MC0", "MC1", "E5") if n in self.config["models"][fold])
        controlled = tuple(self.config.get("controlled_models", {}).get(fold, {}))
        return (
            neural
            + controlled
            + (
                ("ZERO", "M1", "RIDGE_OWN_112", "RIDGE_MARKET_147")
                if fold == "WF1" and partition == "Development"
                else ("ZERO",)
                if partition == "Development"
                else ()
            )
        )

    def result(self, fold: str, model: str) -> dict:
        self.require("READ_SAVED_PREDICTIONS")
        if model not in self.config["models"].get(fold, {}):
            raise ViewUnavailable(f"{model} has no saved {fold} neural run. MC1/E5 are WF1 only.")
        ref = self.config["models"][fold][model]
        obj = read_json(self.root, ref)
        final = obj["final_checkpoint"]
        treatment = self.config.get("controlled_models", {}).get(fold, {}).get(model)
        expected_architecture = "TM0" if treatment is not None else model
        if treatment is not None and (
            obj["contract"].get("arm") != treatment["arm"]
            or obj["contract"]["seed"] != treatment["seed"]
            or obj["contract"].get("amendment") != "TA011_v1"
        ):
            raise ViewUnavailable("Controlled arm/seed identity mismatch.")
        if (
            obj["contract"]["architecture"] != expected_architecture
            or obj["contract"]["stage"] != fold
            or tuple(obj["contract"]["universe"]) != CANDIDATE
            or final["stage"] != "REFIT_FINAL"
            or final["epoch"] != obj["selector"]["selected"]
            or final["pair_key"] != obj["pair_key"]
        ):
            raise ViewUnavailable("Checkpoint/fold/model identity mismatch; comparison rejected.")
        expected = self.config["checkpoints"][fold][model]
        # Reading weight bytes to verify a digest is not deserializing or running the model.
        if local_path(self.root, expected["path"]).exists():
            verified(self.root, expected)
        recipe = self.config["recipes"][fold]["refit"]
        prep = read_preparation(self.root, recipe)
        if final["preparation_id"] != prep.preparation_id:
            # Market/peer arms bind a joined ID; recover it from their frozen input binding.
            if expected_architecture == "TM0":
                raise ViewUnavailable("Checkpoint preprocessing identity mismatch.")
            if final["preparation_id"] != obj["development_population"]["preparation_id"]:
                raise ViewUnavailable("Joined checkpoint preprocessing identity mismatch.")
        if treatment is None and fold in self.config.get("both_pass_health", {}):
            health = read_json(self.root, self.config["both_pass_health"][fold])
            detailed = health if fold == "WF1" else health["health"]
            obj = {**obj, "historical_G6": obj["G6"], "G6": detailed[model]["status"]}
        return obj


def records_frame(records: list[dict], model: str, fold: str, partition: str) -> pd.DataFrame:
    """Saved five-stock origins become compact rows; no inference is performed."""
    rows = []
    for r in records:
        date_window(r["session"], r["session"])
        if len(r["scores"]) != 5 or len(r["targets"]) != 5 or r["origin"] not in (1, 2):
            raise ViewUnavailable("Five-stock prediction snapshot schema mismatch.")
        for symbol, y, score in zip(CANDIDATE, r["targets"], r["scores"]):
            rows.append(
                {
                    "session": r["session"],
                    "origin": r["origin"],
                    "symbol": symbol,
                    "TG0": y,
                    "score": score,
                    "model": model,
                    "fold": fold,
                    "partition": partition,
                }
            )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise ViewUnavailable("No observations recorded for this model/partition.")
    if frame.duplicated(["session", "origin", "symbol"]).any():
        raise ViewUnavailable("Duplicate forecast snapshot keys.")
    if not np.isfinite(frame[["TG0", "score"]].to_numpy()).all():
        raise ViewUnavailable("Nonfinite prediction snapshot.")
    return frame


def predictions(catalog: Catalog, fold: str, model: str, partition: str) -> pd.DataFrame:
    catalog.require("READ_SAVED_PREDICTIONS")
    if model not in catalog.model_names(fold, partition):
        raise ViewUnavailable(f"{model} is not recorded for {fold} / {partition}.")
    if fold == "WF1" and model == "TM0":
        catalog.result(fold, model)
        saved = read_csv(catalog.root, catalog.config["baseline"])
        key = {"Development": "WF1", "Inner validation": "validation", "Refit training": "refit"}[
            partition
        ]
        frame = saved.loc[
            saved.partition == key, ["session", "origin", "symbol", "TG0", "TM0"]
        ].copy()
        frame = frame.rename(columns={"TM0": "score"})
        frame["model"], frame["fold"], frame["partition"] = model, fold, partition
        if frame.empty:
            raise ViewUnavailable("Not recorded: no TM0 snapshot for this partition.")
    elif model in catalog.config["models"][fold]:
        obj = catalog.result(fold, model)
        if partition == "Inner validation":
            trace = catalog.config["traces"][fold][model]["calibration"]
            chosen = obj["selector"]["selected"]
            records = read_json(catalog.root, trace[chosen - 1])["validation"]["origin_records"]
        else:
            key = "development" if partition == "Development" else "refit_train_evaluation"
            records = obj[key]["origin_records"]
        frame = records_frame(records, model, fold, partition)
    elif model == "ZERO":
        frame = predictions(catalog, fold, "TM0", partition).copy()
        frame["score"], frame["model"] = 0.0, model
    elif model == "RIDGE_MARKET_147":
        obj = read_json(catalog.root, catalog.config["market_ridge"])
        truth = predictions(catalog, fold, "TM0", partition)
        keys = list(dict.fromkeys(zip(truth.session, truth.origin)))
        if keys != [tuple(k) for k in obj["origin_keys"]]:
            raise ViewUnavailable("Market ridge mask differs; matched comparison rejected.")
        frame = truth.copy()
        frame["score"], frame["model"] = np.asarray(obj["scores"]).reshape(-1), model
    else:
        saved = read_csv(catalog.root, catalog.config["baseline"])
        frame = saved.loc[saved.partition == "WF1", ["session", "origin", "symbol", "TG0"]].copy()
        frame["score"] = saved.loc[saved.partition == "WF1", model].to_numpy()
        frame["model"], frame["fold"], frame["partition"] = model, fold, partition
    if partition == "Development":
        start, end = catalog.config["development_windows"][fold]
        if not frame.session.between(start, end).all():
            raise ViewUnavailable("Snapshot is outside its declared development fold.")
    frame["residual"] = frame.score - frame.TG0
    if (
        frame.duplicated(["session", "origin", "symbol"]).any()
        or not np.isfinite(frame[["TG0", "score"]].to_numpy()).all()
    ):
        raise ViewUnavailable("Finite unique saved predictions required.")
    frame["squared_error"] = frame.residual**2
    frame["cutoff"] = (
        pd.to_datetime(frame.session + frame.origin.map({1: " 10:30", 2: " 11:30"}))
        .dt.tz_localize(ET)
        .dt.tz_convert("UTC")
    )
    frame["maturity"] = frame.cutoff + pd.Timedelta(hours=4, minutes=3)
    return frame


def source_bars(
    catalog: Catalog, symbol: str, start: str, end: str, interval: str = "30 min source"
) -> tuple[pd.DataFrame, dict]:
    catalog.require("READ_SOURCE")
    symbol_required(symbol)
    lower, upper = date_window(start, end)
    if interval not in {"30 min source", "Completed hour"}:
        raise ViewUnavailable("Choose 30 min source or Completed hour.")
    manifest = read_json(catalog.root, catalog.config["source_manifest"])
    parts, names = [], []
    for ref in manifest["source_by_stock"][symbol]:
        params = ref["params"]
        if pd.Timestamp(params["start"]) >= upper or pd.Timestamp(params["end"]) < lower:
            continue
        path = verified(catalog.root, {"path": ref["data"], "sha256": ref["sha256"]})
        meta = read_json(catalog.root, {"path": ref["manifest"], "sha256": ref["manifest_sha256"]})
        if meta["params"] != params or any(
            params.get(k) != v
            for k, v in {
                "feed": "sip",
                "timeframe": "30Min",
                "currency": "USD",
                "adjustment": "split",
                "asof": "2025-06-30",
            }.items()
        ):
            raise ViewUnavailable("Source interval/feed/adjustment identity mismatch.")
        # Both boundaries and stock predicate are passed before Arrow returns numeric rows.
        frame = pq.read_table(
            path,
            columns=COLUMNS,
            filters=[
                ("symbol", "=", symbol),
                ("timestamp", ">=", lower.to_pydatetime()),
                ("timestamp", "<", upper.to_pydatetime()),
                ("timestamp", "<", BARRIER.to_pydatetime()),
            ],
        ).to_pandas()
        if not frame.empty:
            frame["source_archive"] = ref["data"]
            parts.append(frame)
            names.append(ref["data"])
    if not parts:
        raise ViewUnavailable("No local source observations for these filters.")
    native = pd.concat(parts, ignore_index=True).sort_values("timestamp")
    native = normalize(native, stocks=True)
    require_valid(native, stocks=True)
    if not (
        native.source_timeframe.eq("30Min") & native.feed.eq("sip") & native.adjustment.eq("split")
    ).all():
        raise ViewUnavailable("Native row interval/feed/adjustment mismatch.")
    if native.duplicated(["symbol", "timestamp"]).any() or (native.timestamp >= BARRIER).any():
        raise ViewUnavailable("Duplicate or forbidden source key; view rejected.")
    native = fully_inside_rth(native, start, end)
    if native.empty:
        raise ViewUnavailable("No regular-session observations (holiday/weekend/empty range).")
    if interval == "Completed hour":
        frame, qa = aggregate_session_hours(native, [symbol], start, end)
        frame = frame.loc[~frame.is_stub].copy()
        frame["source_archive"] = "; ".join(names)
        missing = qa["missing_source_bars"]
    else:
        frame = native.copy()
        frame["available_at"] = frame.timestamp + pd.Timedelta(minutes=30)
        frame["session"] = frame.timestamp.dt.tz_convert(ET).dt.strftime("%Y-%m-%d")
        stub_starts = {
            grid["start"]
            for _, row in schedule(start, end).iterrows()
            for grid in session_grid(row.open, row.close)
            if grid["stub"]
        }
        frame["is_stub"] = frame.timestamp.isin(stub_starts)
        frame["duration_minutes"] = 30
        missing = None
    frame["time_ET"] = frame.timestamp.dt.tz_convert(ET).dt.strftime("%Y-%m-%d %H:%M %Z")
    frame["UTC_key"] = frame.timestamp.astype(str)
    return frame, {
        "source_files": names,
        "rows": len(frame),
        "missing_constituents": missing,
        "adjustment": "Vendor retrospective split-price / inverse-volume, USD",
        "availability": "IDEALIZED period end; observed publication not recorded",
        "barrier": str(BARRIER),
        "stub_count": int(frame.is_stub.sum()),
    }


def component_base(catalog: Catalog) -> BaseTables:
    """Single existing compressed canonical store, never raw scans or a second feature DB."""
    catalog.require("READ_FEATURES")
    manifest = read_json(catalog.root, catalog.config["manifest"])
    auth = manifest["authority"]
    authority = load_authority(catalog.root, auth["policy_ref"], auth["approval_ref"])
    return load_tables(authority, manifest["canonical_store"])


def feature_frame(
    catalog: Catalog,
    base: BaseTables,
    symbol: str,
    fold: str,
    start: str,
    end: str,
    origin: int,
    partition: str,
) -> pd.DataFrame:
    lower, upper = date_window(start, end)
    symbol_required(symbol)
    if origin not in (1, 2) or fold not in catalog.config["recipes"]:
        raise ViewUnavailable("Choose a valid feature origin context and fold.")
    key = "inner" if partition == "Inner validation" else "refit"
    prep = read_preparation(catalog.root, catalog.config["recipes"][fold][key])
    view = CandidateView(base, prep)
    floors = next(p for p in prep.floors if p.symbol == symbol)
    rows = []
    for i, step in enumerate(base.history.calendar.steps):
        if not lower <= step.end < upper:
            continue
        native, reasons = raw_features(base, symbol, i, origin, floors)
        scaled = view.row(symbol, i, origin)
        for j, feature in enumerate(ORDER):
            rows.append(
                {
                    "timestamp": step.end,
                    "session": step.session,
                    "feature": feature,
                    "native": native[j],
                    "scaled": float(np.float32(scaled[j])) if scaled else None,
                    "status": reasons[j],
                    "symbol": symbol,
                    "origin_context": origin,
                    "preparation_id": prep.preparation_id,
                    "recipe_stop": str(prep.window.stop),
                }
            )
    return pd.DataFrame(rows)


def market_frame(catalog: Catalog, fold: str, start: str, end: str, partition: str) -> pd.DataFrame:
    lower, upper = date_window(start, end)
    store = json.loads(
        gzip.decompress(verified(catalog.root, catalog.config["market"]).read_bytes())
    )
    key = fold + ("_INNER_TRAIN" if partition == "Inner validation" else "_REFIT")
    recipe = (
        store["preparations"][key]
        if fold == "WF1"
        else read_json(catalog.root, catalog.config["market_recipes"][fold][key])
    )
    rows = []
    for saved in store["measures"]:
        at = pd.Timestamp(saved["timestamp"])
        if not lower <= at < upper:
            continue
        r = dict(saved)
        r["timestamp"] = at
        r["evidence_ids"] = tuple(r["evidence_ids"])
        raw = conditional_vector(MarketMeasures(**r), recipe["hourly_floor"], recipe["daily_floor"])
        if raw is None:
            rows.extend(
                {
                    "timestamp": at,
                    "feature": f"U{j + 1}",
                    "native": None,
                    "scaled": None,
                    "source": "SPY ETF",
                    "valid": False,
                }
                for j in range(5)
            )
            continue
        for j, value in enumerate(raw):
            scaled = (
                0.0
                if recipe["methods"][j] == "CONSTANT"
                else (value - recipe["centers"][j]) / recipe["scales"][j]
            )
            rows.append(
                {
                    "timestamp": at,
                    "feature": f"U{j + 1}",
                    "native": value,
                    "scaled": float(np.float32(scaled)),
                    "source": "SPY ETF",
                    "valid": True,
                }
            )
    return pd.DataFrame(rows)


def event_markers(start: str, end: str, origins: tuple[int, ...]) -> pd.DataFrame:
    date_window(start, end)
    rows = []
    for day in schedule(start, end).index:
        clock = session_clock(str(day.date()))
        for origin in origins:
            plan = execution_plan(clock, origin)
            if plan.calendar_valid:
                rows.append(
                    {
                        "session": str(day.date()),
                        "origin": origin,
                        "cutoff": plan.cutoff,
                        "entry_event": plan.entry,
                        "exit_event": plan.exit,
                        "proxy_exit_close": plan.cutoff + pd.Timedelta(hours=4)
                        if plan.cutoff is not None
                        else None,
                    }
                )
    return pd.DataFrame(rows)


def training_trace(catalog: Catalog, fold: str, model: str) -> pd.DataFrame:
    catalog.require("READ_DIAGNOSTICS")
    obj = catalog.result(fold, model)
    rows = []
    for stage, refs in catalog.config["traces"][fold][model].items():
        for ref in refs:
            record = read_json(catalog.root, ref)
            train = record["training"] if stage == "calibration" else record
            grad = train["gradients"]
            rows.append(
                {
                    "stage": stage,
                    "epoch": train["epoch"],
                    "training_MSE": train["mse"],
                    "inner_validation_MSE": record.get("validation", {}).get("mse"),
                    "clipped_fraction": grad["clipped_fraction"],
                    "grad_p50": grad["median"],
                    "grad_p95": grad["p95"],
                    "grad_max": grad["max"],
                    "nonfinite": grad["nonfinite_count"],
                    "warning": grad["sustained_clipping_warning"],
                    "selected": stage == "calibration"
                    and train["epoch"] == obj["selector"]["selected"],
                    "steps": train["steps"],
                    "optimizer_objective": train.get("optimizer_objective", train["mse"]),
                    "objective_name": train.get("objective_name", "MSE"),
                    "applied_clipping_fraction": grad.get(
                        "applied_clipping_fraction", grad["clipped_fraction"]
                    ),
                    "fraction_above5": grad.get("fraction_above5"),
                }
            )
    return pd.DataFrame(rows)


def gradient_batches(catalog: Catalog, fold: str, model: str, stage: str) -> pd.DataFrame:
    catalog.require("READ_DIAGNOSTICS")
    controlled = catalog.config.get("controlled_telemetry", {}).get(fold, {}).get(model)
    if controlled is not None:
        if stage not in {"calibration", "refit"}:
            raise ViewUnavailable("Choose calibration or refit.")
        return read_csv(catalog.root, controlled[stage])
    if fold != "WF2" or model not in ("TM0", "MC0"):
        raise ViewUnavailable(
            "Not recorded: WF1 has aggregate epoch norms, no paired batch history."
        )
    if stage not in {"calibration", "refit"}:
        raise ViewUnavailable("Choose calibration or refit.")
    return read_csv(catalog.root, catalog.config["batch_telemetry"][model][stage])


def target_details(
    catalog: Catalog, base: BaseTables, fold: str, partition: str, frame: pd.DataFrame
) -> pd.DataFrame:
    """Existing canonical return/MAD/TG0 implementation; no floor fitting or price invention."""
    from ..pretraining_tables import tg0

    key = "inner" if partition == "Inner validation" else "refit"
    prep = read_preparation(catalog.root, catalog.config["recipes"][fold][key])
    rows = []
    for (day, origin), group in frame.groupby(["session", "origin"], sort=True):
        date_window(str(day), str(day))
        if not isinstance(origin, (int, np.integer)) or origin not in (1, 2):
            raise ViewUnavailable("Integer forecast-origin type required.")
        panel = base.panels[str(day), int(origin)]
        moments = panel.median_mad
        if moments is None:
            raise ViewUnavailable("Mature target decomposition unavailable.")
        values = tuple(v for v in panel.returns if v is not None)
        y = np.asarray(tg0(values, prep.target_epsilon), dtype=np.float32)
        median, mad = moments
        for r in group.itertuples():
            j = CANDIDATE.index(str(r.symbol))
            if abs(float(y[j]) - numeric(r.TG0)) > 2e-6:
                raise ViewUnavailable("Saved target / recipe decomposition mismatch.")
            rows.append(
                {
                    "session": str(day),
                    "origin": int(origin),
                    "symbol": r.symbol,
                    "log_return": values[j],
                    "median": median,
                    "MAD": mad,
                    "epsilon": prep.target_epsilon,
                    "denominator": mad + prep.target_epsilon,
                    "numerator": values[j] - median,
                    "TG0": float(y[j]),
                    "floor_ge_MAD": prep.target_epsilon >= mad,
                    "maturity": str(panel.maturity),
                    "partition": partition,
                }
            )
    return pd.DataFrame(rows)


def peer_window(
    catalog: Catalog,
    base: BaseTables,
    fold: str,
    day: str,
    origin: int,
    symbol: str,
    partition: str,
) -> pd.DataFrame:
    from ..peer_inputs import peer_summaries

    date_window(day, day)
    symbol_required(symbol)
    key = "inner" if partition == "Inner validation" else "refit"
    prep = read_preparation(catalog.root, catalog.config["recipes"][fold][key])
    view = CandidateView(base, prep)
    values, _ = view.window(day, origin)
    peers = peer_summaries(values.astype(np.float32))[CANDIDATE.index(symbol)]
    positions = base.origin_steps[day, origin]
    return pd.DataFrame(
        {
            "timestamp": [base.history.calendar.steps[i].end for i in positions],
            "four_peer_M1_mean": peers[:, 0],
            "four_peer_M1_population_SD": peers[:, 1],
        }
    )


def saved_gates(catalog: Catalog) -> list[dict]:
    """Only the exact evaluated gate examples already captured by Package008."""
    cases = read_json(catalog.root, catalog.config["saved_gate_examples"])["cases"]
    expected = catalog.result("WF1", "MC1")["final_checkpoint"]["sha256"]
    for case in cases:
        date_window(case["key"][0], case["key"][0])
        if case["B4_B5"]["MC1"]["checkpoint_sha"] != expected:
            raise ViewUnavailable("Saved gate example checkpoint changed.")
    return cases
