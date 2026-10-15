"""Package010B read-only, exact-mask views of the sealed Package011 study.

No fitting, checkpoint execution or alternate transform estimation is exposed.
Display transforms use existing parameter IDs; saved predictions are canonical.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from ..ft0_transforms import ORDER, SCALED, identity
from ..pretraining_policy import CANDIDATE
from ..pretraining_store import read_preparation
from ..pretraining_tables import BaseTables, tg0
from ..pretraining_transforms import CandidateView, canonical_population, raw_features
from ..stock_source import numeric
from .loaders import (
    PARTITIONS,
    Catalog,
    ViewUnavailable,
    date_window,
    predictions,
    read_csv,
    read_json,
    training_trace,
    verified,
)
from .metrics import matched, summary

ARMS = ("C0", "H1", "T1", "T2", "O1")
OBJECTIVES = {
    "C0": "Canonical TG0 squared error",
    "H1": "Huber delta 2 on canonical TG0 (Huber objective units)",
    "T1": "Squared error against clipped TG0 optimizer labels",
    "T2": "Squared error in asinh(TG0/s) units",
    "O1": "Canonical TG0 squared error; gradient cap 5",
}
KEYS = ["session", "origin", "symbol"]


def arm_model(arm: str, seed: int) -> str:
    if arm not in ARMS or seed not in (42, 123):
        raise ViewUnavailable("Not recorded: choose a registered Package011 arm and seed.")
    return "TM0" if (arm, seed) == ("C0", 42) else f"{arm} [{seed}]"


def exact_match(left: pd.DataFrame, right: pd.DataFrame) -> None:
    """No intersection/drop policy: keys, canonical targets and clocks must match exactly."""
    for frame in (left, right):
        if frame.empty or frame.duplicated(KEYS).any():
            raise ViewUnavailable("NOT_COMPARABLE: missing or duplicate observation keys.")
        if not np.isfinite(frame[["TG0", "score"]].to_numpy()).all():
            raise ViewUnavailable("NOT_COMPARABLE: nonfinite saved scores/targets.")
        for _, group in frame.groupby(["session", "origin"]):
            if len(group) != 5 or set(group.symbol) != set(CANDIDATE):
                raise ViewUnavailable("NOT_COMPARABLE: incomplete five-stock mask.")
    try:
        matched(left, right)
    except ViewUnavailable as exc:
        raise ViewUnavailable(f"NOT_COMPARABLE: {exc}") from exc
    a, b = left.sort_values(KEYS), right.sort_values(KEYS)
    for clock in ("cutoff", "maturity"):
        if clock not in a or clock not in b or not np.array_equal(a[clock], b[clock]):
            raise ViewUnavailable("NOT_COMPARABLE: differing or missing origin timestamps.")


@dataclass(frozen=True)
class Study:
    catalog: Catalog
    refs: dict[str, dict]

    @classmethod
    def discover(cls, catalog: Catalog) -> Study:
        binding = catalog.config.get("controlled_explorer")
        if binding is None:
            raise ViewUnavailable("Not recorded: Package010B study binding unavailable.")
        seal = read_json(catalog.root, binding["seal"])
        refs = {r["path"].rsplit("/", 1)[-1]: r for r in seal["artifacts"]}
        study = cls(catalog, refs)
        plan = study.json("predeclared_experiment_matrix_corrected.json")
        if binding["proposal_sha256"] != catalog.config["controlled_package"]["proposal_sha256"]:
            raise ViewUnavailable("NOT_COMPARABLE: stale study proposal identity.")
        verified(
            catalog.root,
            {
                **refs["predeclared_experiment_matrix_corrected.json"],
                "sha256": binding["proposal_sha256"],
            },
        )
        inputs = study.json("input_binding.json")
        if inputs["source"] != catalog.config["manifest"] or inputs["confirmation_numeric_rows"]:
            raise ViewUnavailable("NOT_COMPARABLE: source or protected-data identity mismatch.")
        if not plan:
            raise ViewUnavailable("NOT_COMPARABLE: missing sealed study plan.")
        for fold in ("WF1", "WF2"):
            for prefix, key in (("INNER_TRAIN", "inner"), ("REFIT", "refit")):
                ref = inputs["stock_preparations"][fold][f"{fold}_{prefix}"]
                current = catalog.config["recipes"][fold][key]
                if any(ref[k] != current[k] for k in ("path", "sha256")):
                    raise ViewUnavailable("NOT_COMPARABLE: stale fold/preparation reference.")
                prep = read_preparation(catalog.root, current)
                if prep.preparation_id != ref["preparation_id"]:
                    raise ViewUnavailable("NOT_COMPARABLE: preprocessing identity mismatch.")
        return study

    def json(self, name: str) -> dict:
        if name not in self.refs:
            raise ViewUnavailable(f"Not recorded: {name} is absent from the study seal.")
        return read_json(self.catalog.root, self.refs[name])

    def table(self, name: str) -> pd.DataFrame:
        if name not in self.refs:
            raise ViewUnavailable(f"Not recorded: {name} is absent from the study seal.")
        return read_csv(self.catalog.root, self.refs[name])

    def parameter(self, fold: str, arm: str, prefix: str) -> dict:
        arm_model(arm, 42)
        if fold not in ("WF1", "WF2") or prefix not in ("inner", "refit"):
            raise ViewUnavailable("Only registered inner/refit training prefixes are permitted.")
        value = self.json("target_parameter_bindings.json")[fold][arm][prefix]
        contents = {k: v for k, v in value.items() if k != "parameter_id"}
        prep = read_preparation(self.catalog.root, self.catalog.config["recipes"][fold][prefix])
        if (
            identity(contents) != value["parameter_id"]
            or value["preparation_id"] != prep.preparation_id
            or value["cutoff"] != str(prep.window.stop)
            or value["policy"]["arm"] != arm
            or value["scale_floor"] != 1e-6
        ):
            raise ViewUnavailable("NOT_COMPARABLE: immutable training parameter identity failed.")
        return value

    def panel(self, fold: str, seed: int, arm: str, partition: str) -> pd.DataFrame:
        if fold not in ("WF1", "WF2") or partition not in PARTITIONS:
            raise ViewUnavailable("Only three recorded preconfirmation partitions are permitted.")
        model = arm_model(arm, seed)
        result = self.catalog.result(fold, model)
        if result["contract"]["seed"] != seed or result.get("confirmation_numeric_rows", 0):
            raise ViewUnavailable("NOT_COMPARABLE: result seed/protected-data contract mismatch.")
        if (arm, seed) != ("C0", 42):
            for prefix in ("inner", "refit"):
                if result["target_parameters"][prefix] != self.parameter(fold, arm, prefix):
                    raise ViewUnavailable("NOT_COMPARABLE: result training parameter mismatch.")
        frame = predictions(self.catalog, fold, model, partition)
        control = predictions(self.catalog, fold, "TM0", partition)
        exact_match(frame, control)
        if partition == "Development":
            original = self.json("input_binding.json")["canonical_outer_panels"][fold]
            canonical = pd.DataFrame(
                [
                    (day, origin, symbol, float(np.float32(value)))
                    for day, origin, values in original
                    for symbol, value in zip(CANDIDATE, values)
                ],
                columns=[*KEYS, "TG0"],
            ).sort_values(KEYS)
            ordered = frame.sort_values(KEYS)
            if (
                canonical.duplicated(KEYS).any()
                or list(canonical[KEYS].itertuples(index=False, name=None))
                != list(ordered[KEYS].itertuples(index=False, name=None))
                or not np.array_equal(canonical.TG0, ordered.TG0)
            ):
                raise ViewUnavailable("NOT_COMPARABLE: original outer target identity differs.")
            saved = self.table("predictions_long.csv")
            saved = saved.loc[(saved.fold == fold) & (saved.seed == seed) & (saved.arm == arm)]
            a, b = frame.sort_values(KEYS), saved.sort_values(KEYS)
            if (
                b.duplicated(KEYS).any()
                or list(a[KEYS].itertuples(index=False, name=None))
                != list(b[KEYS].itertuples(index=False, name=None))
                or not np.array_equal(a.TG0, b.observed_canonical_TG0)
                or not np.array_equal(a.score, b.canonical_predicted_TG0)
                or not np.array_equal(pd.to_datetime(b.origin_timestamp, utc=True), a.cutoff)
            ):
                raise ViewUnavailable(
                    "NOT_COMPARABLE: sealed canonical forecast/target/clock mismatch."
                )
        frame["arm"], frame["seed"] = arm, seed
        frame["run_id"] = self.run_id(fold, seed, arm)
        return frame

    def run_id(self, fold: str, seed: int, arm: str) -> str:
        if (arm, seed) == ("C0", 42):
            return f"C0-S42-{fold} (reused {self.catalog.result(fold, 'TM0')['pair_key']})"
        registry = self.table("experiment_registry.csv")
        rows = registry.loc[
            (registry.fold == fold) & (registry.seed == seed) & (registry.arm == arm)
        ]
        if len(rows) != 1 or rows.iloc[0].status != "COMPLETED":
            raise ViewUnavailable("Not recorded: exactly one completed study identity required.")
        return str(rows.iloc[0].run_id)

    def training_targets(self, base: BaseTables, fold: str, prefix: str) -> pd.DataFrame:
        """Reconstruct only existing TG0 labels, and prove exact registered population hash.

        This calculates no fitted quantity. The registered float64 population identity
        must agree before any display transform is applied.
        """
        param = self.parameter(fold, "T2", prefix)
        prep = read_preparation(self.catalog.root, self.catalog.config["recipes"][fold][prefix])
        prep.ensure(base)
        keys, _ = canonical_population(base, prep.window)
        population = []
        rows = []
        for day, origin in keys:
            panel = base.panels[day, origin]
            values = tg0(tuple(v for v in panel.returns if v is not None), prep.target_epsilon)
            population.append((day, origin, values))
            for symbol, value in zip(CANDIDATE, values):
                rows.append(dict(session=day, origin=origin, symbol=symbol, TG0=value))
        if (
            identity(population) != param["target_population_hash"]
            or len(rows) != param["observations"]
        ):
            raise ViewUnavailable(
                "NOT_COMPARABLE: reconstructed training label population differs."
            )
        return pd.DataFrame(rows)

    def trace(self, fold: str, seed: int, arm: str) -> pd.DataFrame:
        model = arm_model(arm, seed)
        frame = training_trace(self.catalog, fold, model)
        for column in ("grad_p90", "grad_p99"):
            frame[column] = np.nan
        for stage, refs in self.catalog.config["traces"][fold][model].items():
            for ref in refs:
                record = read_json(self.catalog.root, ref)
                record = record["training"] if stage == "calibration" else record
                grad = record["gradients"]
                mask = (frame.stage == stage) & (frame.epoch == record["epoch"])
                frame.loc[mask, "grad_p90"] = grad.get("p90", np.nan)
                frame.loc[mask, "grad_p99"] = grad.get("p99", np.nan)
                # Legacy aggregate exceedance is not observed applied clipping.
                if "applied_clipping_fraction" not in grad:
                    frame.loc[mask, "applied_clipping_fraction"] = np.nan
        return frame


def label_views(targets: pd.Series, t1: dict, t2: dict) -> pd.DataFrame:
    """Display existing fitted target transforms; never invert a saved forecast."""
    cap, scale = float(t1["policy"]["cap"]), float(t2["policy"]["scale"])
    if not np.isfinite((cap, scale)).all() or min(cap, scale) <= 0:
        raise ViewUnavailable("Invalid registered cap/scale.")
    raw = targets.to_numpy(dtype=float)
    return pd.DataFrame(
        {
            "Original TG0": raw,
            "T1 clipped TG0 optimizer label": np.clip(raw, -cap, cap),
            "T2 asinh optimizer label": np.arcsinh(raw / scale),
        }
    )


def quantiles(values: pd.Series) -> dict:
    finite = values[np.isfinite(values)]
    if finite.empty:
        return {"finite": 0, "missing/nonfinite": len(values)}
    q = finite.quantile([0, 0.01, 0.5, 0.99, 0.999, 1]).to_list()
    return dict(
        zip(("min", "p1", "p50", "p99", "p99.9", "max"), q),
        finite=len(finite),
        **{"missing/nonfinite": len(values) - len(finite)},
    )


def paired_table(
    control: pd.DataFrame, treatment: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    exact_match(control, treatment)
    zero = control.assign(score=0.0, squared_error=control.TG0**2)
    rows, daily = [], []
    for name, frame in (("C0", control), ("Treatment", treatment), ("ZERO", zero)):
        stats = summary(frame)
        rows.append(
            {
                "forecast": name,
                **{
                    k: stats[k]
                    for k in (
                        "MSE",
                        "daily_Rank_IC",
                        "days",
                        "origins",
                        "stock_rows",
                        "defined_origins",
                    )
                },
            }
        )
        daily.append(stats["daily"].set_index("session").add_suffix("_" + name))
    table = pd.DataFrame(rows).set_index("forecast")
    for ref in ("C0", "ZERO"):
        table[f"MSE minus {ref}"] = table.MSE - numeric(table.at[ref, "MSE"])
        table[f"IC minus {ref}"] = table.daily_Rank_IC - numeric(table.at[ref, "daily_Rank_IC"])
    days = pd.concat(daily, axis=1, join="outer")
    days["delta_MSE"] = days.MSE_Treatment - days.MSE_C0
    days["delta_IC"] = days.IC_Treatment - days.IC_C0
    return table.reset_index(), days.reset_index()


def event_state(row: pd.Series, fold: str, seed: int, arm: str, partition: str) -> dict:
    """Set every price-page filter from one verified saved event, including its origin."""
    day, symbol, origin = str(row.session), str(row.symbol), int(row.origin)
    date_window(day, day)
    if symbol not in CANDIDATE or origin not in (1, 2) or partition not in PARTITIONS:
        raise ViewUnavailable("Invalid event navigation context.")
    model = arm_model(arm, seed)
    return dict(
        section="Price & Features",
        fold=fold,
        model=model,
        partition=partition,
        symbol=symbol,
        dates=(date.fromisoformat(day), date.fromisoformat(day)),
        origin_label="10:30 ET" if origin == 1 else "11:30 ET",
        feature_origin=origin,
        price_markers=True,
        selected_study_event=dict(
            session=day,
            symbol=symbol,
            origin=origin,
            fold=fold,
            seed=seed,
            arm=arm,
            partition=partition,
        ),
    )


def input_context(
    catalog: Catalog,
    base: BaseTables,
    fold: str,
    partition: str,
    symbol: str,
    day: str,
    origin: int,
) -> pd.DataFrame:
    """Actual approved 48-step input context, not a newly estimated normalizer."""
    date_window(day, day)
    legal = predictions(catalog, fold, "TM0", partition)
    if legal.loc[
        (legal.session == day) & (legal.origin == origin) & (legal.symbol == symbol)
    ].empty:
        raise ViewUnavailable("Not recorded: event is outside the saved partition mask.")
    prefix = "inner" if partition == "Inner validation" else "refit"
    prep = read_preparation(catalog.root, catalog.config["recipes"][fold][prefix])
    view = CandidateView(base, prep)
    if not view.input_status(day, origin)[0]:
        raise ViewUnavailable("Not recorded: complete 48-step FT0 context unavailable.")
    floors = next(v for v in prep.floors if v.symbol == symbol)
    rows = []
    positions = base.origin_steps[day, origin]
    if len(positions) != 48:
        raise ViewUnavailable("Exactly 48 scheduled full-hour inputs required.")
    for pos in positions:
        native, _ = raw_features(base, symbol, pos, origin, floors)
        scaled = view.row(symbol, pos, origin)
        if scaled is None:
            raise ViewUnavailable("Not recorded: input context incomplete.")
        step = base.history.calendar.steps[pos]
        for j, feature in enumerate(ORDER):
            rows.append(
                dict(
                    timestamp=step.end,
                    feature=feature,
                    native=native[j],
                    scaled=float(np.float32(scaled[j])),
                    symbol=symbol,
                    preparation_id=prep.preparation_id,
                )
            )
    return pd.DataFrame(rows)


def feature_parameters(
    catalog: Catalog, fold: str, partition: str, symbol: str, feature: str
) -> dict:
    if feature not in ORDER or partition not in PARTITIONS or symbol not in CANDIDATE:
        raise ViewUnavailable("Select a recorded feature/partition/stock.")
    prefix = "inner" if partition == "Inner validation" else "refit"
    ref = catalog.config["recipes"][fold][prefix]
    prep = read_preparation(catalog.root, ref)
    floor = next(v for v in prep.floors if v.symbol == symbol)
    values = dict(
        recipe=ref,
        preparation_id=prep.preparation_id,
        fitted_stop=str(prep.window.stop),
        fitted_at=str(prep.window.fitted_at),
        hourly_floor=floor.hourly_floor,
        daily_floor=floor.daily_floor,
        m2_floor=floor.m2_floor,
        hourly_pseudocount=floor.hourly_pseudocount,
        daily_pseudocount=floor.daily_pseudocount,
    )
    if feature in SCALED:
        j = SCALED.index(feature)
        values.update(
            center=prep.scaler.centers[j],
            scale=prep.scaler.scales[j],
            method=prep.scaler.methods[j],
            formula="(native − center) / scale",
        )
    else:
        values.update(method="NATIVE_BOUNDED_IDENTITY", formula="scaled = native; float32 input")
    return values
