"""Independent S2-C calibration, score persistence and descriptive evaluation.

Authority: EXPERIMENT_SPEC.md §§14–15. No project helper, historical score,
comparator, market-data reader, or model-training function is used here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray
import pandas as pd


STOCKS = (
    "VZ", "COP", "BAC", "BA", "AAPL", "PEP", "MRK", "SBUX", "CVX", "MS",
    "AMD", "KO", "JNJ", "AMZN", "XOM", "WFC", "AVGO", "TSLA", "MA", "CSCO",
)
CATEGORIES = ("INTRADAY", "OVERNIGHT")
MODELS = ("S2C-RAW", "S2C-C3")
TIMESTAMPS = ("entry_end_utc", "exit_end_utc", "label_maturity_utc")
KEY_FIELDS = ("origin_id", "ticker", "session_date_et", "slot", "category", *TIMESTAMPS)
BASE_FIELDS = (*KEY_FIELDS, "weight", "A")
SCORE_FIELDS = (*BASE_FIELDS, "Mhat", *MODELS)
SIGNED_COMPONENTS = ("pre", "gap", "post")
RANK_FIELDS = (
    "spearman_ic", "pair_concordance", "tie_rate", "constant_rate",
    "top4_retrieval", "bottom4_retrieval",
)
SCALAR_FIELDS = ("observed", "predicted", "bias", "mae", "mse", "ratio")
EVENT_FIELDS = ("prevalence", "top4_recall", "top4_precision", "false_low_rank")
FloatArray = NDArray[np.float64]


def _vector(values: ArrayLike, name: str, *, nonnegative: bool = False) -> FloatArray:
    result = np.asarray(values, dtype=np.float64)
    if result.ndim != 1 or not np.isfinite(result).all():
        raise ValueError(f"{name} must be a finite one-dimensional array")
    if nonnegative and (result < 0).any():
        raise ValueError(f"{name} must be nonnegative")
    return result


def _positive_scale(scale: float) -> float:
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("scale must be finite and strictly positive")
    return float(scale)


def _utc(value: object, name: str) -> pd.Timestamp:
    # Conversion must not silently interpret a naive datetime as UTC.
    if not isinstance(value, (str, pd.Timestamp)):
        value = str(value)
    stamp = pd.Timestamp(value)
    if pd.isna(stamp) or stamp.tzinfo is None:
        raise ValueError(f"{name} must be an aware timestamp")
    normalized = stamp.tz_convert("UTC").as_unit("ns")
    if not isinstance(normalized, pd.Timestamp):
        raise ValueError(f"{name} must be a nonmissing aware timestamp")
    return normalized


def _frame_digest(rows: pd.DataFrame) -> str:
    serialized = rows.to_json(orient="records", date_format="iso", date_unit="ns", double_precision=15)
    if not isinstance(serialized, str):
        raise TypeError("dataframe serialization must return text")
    return sha256(serialized.encode()).hexdigest()


def _ratio(numerator: float, denominator: float) -> float:
    # Undefined quantities stay NaN/inf rather than receiving an invented zero.
    with np.errstate(divide="ignore", invalid="ignore"):
        return float(np.divide(numerator, denominator))


def _mean_valid(values: ArrayLike) -> float:
    array = np.asarray(values, dtype=np.float64)
    valid = ~np.isnan(array)
    return float(np.mean(array[valid])) if valid.any() else float("nan")


def weighted_left_quantile(values: ArrayLike, weights: ArrayLike, q: float) -> float:
    """First ascending observation whose normalized cumulative weight reaches q."""
    values_array = _vector(values, "quantile values")
    weight_array = _vector(weights, "quantile weights")
    if len(values_array) == 0 or values_array.shape != weight_array.shape:
        raise ValueError("quantile values and weights need matching nonempty shape")
    if not 0 <= q <= 1 or (weight_array <= 0).any():
        raise ValueError("quantile needs q in [0,1] and strictly positive weights")
    order = np.argsort(values_array, kind="stable")
    cumulative = np.cumsum(weight_array[order], dtype=np.float64)
    cumulative /= cumulative[-1]
    index = min(int(np.searchsorted(cumulative, q, side="left")), len(order) - 1)
    return float(values_array[order[index]])


def hierarchy_weights(rows: pd.DataFrame) -> FloatArray:
    """Equal sessions, then origins, then twenty cells, for one supplied role."""
    if rows.empty:
        raise ValueError("cannot weight an empty role")
    counts = rows.groupby("origin_id", sort=False).size()
    if not (counts == 20).all():
        raise ValueError("each origin must have exactly twenty stock cells")
    origin_dates = rows.groupby("origin_id", sort=False)["session_date_et"]
    if not (origin_dates.nunique() == 1).all():
        raise ValueError("an origin cannot span session dates")
    dates = rows[["origin_id", "session_date_et"]].drop_duplicates()
    per_day = dates.groupby("session_date_et", sort=False).size()
    sessions = len(per_day)
    return np.asarray(
        [1.0 / (sessions * int(per_day.loc[day]) * 20) for day in rows["session_date_et"]],
        dtype=np.float64,
    )


def canonical_rows(
    rows: pd.DataFrame, *, require_scores: bool = False, check_weights: bool = True,
    require_order: bool = False,
) -> pd.DataFrame:
    """Validate complete twenty-name origins and return chronological stock order.

    Original labels/weights are retained. Timestamps are represented as aware UTC
    nanoseconds, and origin identifiers use UTC ISO spelling for full-key joins.
    Weights are checked separately for each year when a multi-year table is given.
    """
    required = SCORE_FIELDS if require_scores else BASE_FIELDS
    missing = [name for name in required if name not in rows]
    if missing or rows.empty:
        raise ValueError(f"missing score fields {missing}, or empty population")
    result = rows.copy(deep=True)
    for column in TIMESTAMPS:
        result[column] = pd.DatetimeIndex([_utc(v, column) for v in result[column]])
    origins = [_utc(v, "origin_id") for v in result["origin_id"]]
    result["origin_id"] = [stamp.isoformat() for stamp in origins]
    if result[["origin_id", "ticker"]].duplicated().any():
        raise ValueError("duplicate (origin_id,ticker) score key")
    if set(result["ticker"]) != set(STOCKS):
        raise ValueError("score population must use the literal twenty-stock universe")
    if not result["category"].isin(CATEGORIES).to_numpy(dtype=bool).all():
        raise ValueError("unknown schedule category")
    local = pd.DatetimeIndex(origins).tz_convert("America/New_York")
    if list(local.strftime("%Y-%m-%d")) != list(result["session_date_et"]):
        raise ValueError("session_date_et does not match origin's Eastern date")
    if list(local.strftime("%H:%M")) != list(result["slot"]):
        raise ValueError("slot does not match origin's Eastern clock")
    if not result["slot"].isin([f"{hour:02}:30" for hour in range(9, 16)]).to_numpy(dtype=bool).all():
        raise ValueError("origin has an unscheduled clock slot")
    if not (result["exit_end_utc"] > result["entry_end_utc"]).all():
        raise ValueError("endpoint must be after entry")
    if not (result["label_maturity_utc"] == result["exit_end_utc"] + pd.Timedelta(minutes=2)).all():
        raise ValueError("label maturity must equal endpoint plus two minutes")
    exit_dates = result["exit_end_utc"].dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d")
    inferred = np.where(exit_dates.to_numpy() == result["session_date_et"].to_numpy(), "INTRADAY", "OVERNIGHT")
    if not np.array_equal(inferred, result["category"].to_numpy()):
        raise ValueError("category must follow endpoint schedule geometry")
    for column in ("A", "weight", *(("Mhat", *MODELS) if require_scores else ())):
        values = _vector(result[column].to_numpy(), column, nonnegative=column != "Mhat")
        result[column] = values
    if (result["weight"] <= 0).any():
        raise ValueError("every primary cell needs positive original weight")
    if require_scores:
        result["Mhat"] = result["Mhat"].astype(np.float32)
        if not np.isfinite(result["Mhat"].to_numpy()).all():
            raise ValueError("Mhat overflows float32")
    constant_fields = ("session_date_et", "slot", "category", *TIMESTAMPS)
    for origin, subset in result.groupby("origin_id", sort=False):
        if len(subset) != 20 or set(subset["ticker"]) != set(STOCKS):
            raise ValueError(f"incomplete twenty-stock origin: {origin}")
        if any(subset[column].nunique(dropna=False) != 1 for column in constant_fields):
            raise ValueError("origin metadata must agree across twenty stocks")
        if "early_close" in subset:
            if subset["early_close"].nunique(dropna=False) != 1 or not subset["early_close"].isin([True, False]).to_numpy(dtype=bool).all():
                raise ValueError("early_close must be a boolean constant within origin")
    result["year"] = [stamp.year for stamp in local]
    if check_weights:
        for _, subset in result.groupby("year", sort=True):
            expected = hierarchy_weights(subset)
            if not np.allclose(subset["weight"].to_numpy(), expected, atol=1e-15, rtol=1e-12):
                raise ValueError("weights differ from original annual primary hierarchy")
    before = list(zip(result["origin_id"], result["ticker"]))
    stock_index = {ticker: index for index, ticker in enumerate(STOCKS)}
    result["_stock_order"] = result["ticker"].map(lambda ticker: stock_index[str(ticker)])
    result = result.sort_values(["origin_id", "_stock_order"], kind="stable").drop(columns="_stock_order").reset_index(drop=True)
    if require_order and before != list(zip(result["origin_id"], result["ticker"])):
        raise ValueError("scores must be stored origin-major then literal stock-major")
    return result


@dataclass(frozen=True)
class ModelIdentity:
    """Digests of the exact restricted-refit recipe and checkpoint."""

    recipe_sha256: str
    checkpoint_sha256: str

    def __post_init__(self) -> None:
        for value in (self.recipe_sha256, self.checkpoint_sha256):
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise ValueError("model identity requires lowercase SHA-256 digests")


@dataclass(frozen=True)
class ContributionDiagnostic:
    rows: int
    q_max: float
    top10_share: float
    top1pct_share: float


@dataclass(frozen=True)
class CategoryCalibration:
    category: str
    moment: float
    effective_sessions: float
    rho: float
    factor: float
    sessions: int
    original_mass: float
    contributions: ContributionDiagnostic


@dataclass(frozen=True)
class C3Calibration:
    """Immutable coefficients fit only from the admitted calibration population."""

    scale: float
    global_moment: float
    categories: tuple[CategoryCalibration, ...]
    identity: ModelIdentity
    role_cutoff_utc: str
    finalized_at_utc: str
    maximum_label_maturity_utc: str
    population_sha256: str
    contributions: ContributionDiagnostic
    kappa: float = 25.0

    def factor(self, category: str) -> float:
        for group in self.categories:
            if group.category == category:
                return group.factor
        raise ValueError(f"unknown category {category}")


def _contributions(q: FloatArray, weight: FloatArray) -> ContributionDiagnostic:
    contributions = np.sort(weight * q)[::-1]
    total = float(contributions.sum())
    if not math.isfinite(total) or total <= 0:
        raise ValueError("residual contributions must sum to finite positive mass")
    return ContributionDiagnostic(
        rows=len(q), q_max=float(q.max()),
        top10_share=float(contributions[:10].sum() / total),
        top1pct_share=float(contributions[:max(1, len(q) // 100)].sum() / total),
    )


def decode_raw(mhat: ArrayLike, scale: float) -> FloatArray:
    """Diagnostic RAW decoder, with clamp on Mhat only in this decoder."""
    output = _vector(mhat, "Mhat")
    with np.errstate(over="raise", invalid="raise"):
        prediction = _positive_scale(scale) * np.expm1(np.maximum(output, 0))
    if not np.isfinite(prediction).all():
        raise ValueError("RAW decoding produced a nonfinite prediction")
    return prediction


def fit_c3(
    calibration_rows: pd.DataFrame, scale: float, identity: ModelIdentity, *,
    role_cutoff_utc: str | pd.Timestamp, finalized_at_utc: str | pd.Timestamp,
) -> C3Calibration:
    """Fit unclamped transformed residuals; shrink by effective session count."""
    rows = canonical_rows(calibration_rows)
    if rows["year"].nunique() != 1:
        raise ValueError("one calibration role must be in one calendar year")
    scale = _positive_scale(scale)
    if "Mhat" not in rows:
        raise ValueError("calibration forecasts Mhat are required")
    # The caller's network emits float32; promote it for float64 residual arithmetic.
    mhat32 = np.asarray(rows["Mhat"], dtype=np.float32)
    mhat = _vector(mhat32, "calibration Mhat")
    actual = _vector(rows["A"].to_numpy(), "calibration A", nonnegative=True)
    weight = _vector(rows["weight"].to_numpy(), "calibration weight")
    cutoff = _utc(role_cutoff_utc, "calibration cutoff")
    finalization = _utc(finalized_at_utc, "calibration finalization")
    max_maturity = _utc(rows["label_maturity_utc"].max(), "maximum maturity")
    if not (rows["label_maturity_utc"] < cutoff).all():
        raise ValueError("calibration contains labels not strictly mature before cutoff")
    if finalization < max_maturity:
        raise ValueError("calibration cannot be finalized before its last admitted label matures")
    with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
        q = np.exp(np.log1p(actual / scale) - mhat)
    if not np.isfinite(q).all() or (q <= 0).any():
        raise ValueError("C3 residual q must remain finite and strictly positive")
    global_moment = float(np.dot(weight, q) / weight.sum())
    if not math.isfinite(global_moment) or global_moment <= 0:
        raise ValueError("global smearing moment must be finite and positive")
    groups: list[CategoryCalibration] = []
    for category in CATEGORIES:
        mask = rows["category"].to_numpy() == category
        if not mask.any():
            raise ValueError(f"calibration category {category} is empty")
        group_weight, group_q = weight[mask], q[mask]
        masses = rows.loc[mask].groupby("session_date_et", sort=True)["weight"].sum().to_numpy(dtype=np.float64)
        if (masses <= 0).any() or not np.isfinite(masses).all():
            raise ValueError("category session masses must be finite positive")
        probabilities = masses / masses.sum()
        neff = float(1.0 / np.dot(probabilities, probabilities))
        rho = neff / (neff + 25.0)
        moment = float(np.dot(group_weight, group_q) / group_weight.sum())
        factor = global_moment + rho * (moment - global_moment)
        if not math.isfinite(factor) or factor <= 0:
            raise ValueError("category smearing factor must be finite positive")
        groups.append(CategoryCalibration(category, moment, neff, rho, factor, len(masses), float(group_weight.sum()), _contributions(group_q, group_weight)))
    audit_rows = rows[[*BASE_FIELDS, "Mhat"]].copy()
    if not isinstance(audit_rows, pd.DataFrame):
        raise TypeError("calibration receipt requires a table of named fields")
    audit_rows["Mhat"] = mhat32
    population_digest = _frame_digest(audit_rows)
    return C3Calibration(
        scale, global_moment, tuple(groups), identity, cutoff.isoformat(), finalization.isoformat(),
        max_maturity.isoformat(), population_digest, _contributions(q, weight),
    )


def decode_c3(
    mhat: ArrayLike, categories: Sequence[str] | NDArray[np.str_],
    calibration: C3Calibration, identity: ModelIdentity,
) -> FloatArray:
    """Apply frozen C3 coefficients with exact recipe/checkpoint identity checks."""
    if identity != calibration.identity:
        raise ValueError("calibration and OOS must use the same frozen recipe/checkpoint")
    output = _vector(mhat, "Mhat")
    if len(categories) != len(output):
        raise ValueError("categories and Mhat need matching lengths")
    factors = np.asarray([calibration.factor(str(category)) for category in categories], dtype=np.float64)
    with np.errstate(over="raise", invalid="raise"):
        prediction = calibration.scale * np.maximum(0, np.exp(output) * factors - 1)
    if not np.isfinite(prediction).all():
        raise ValueError("C3 decoding produced a nonfinite prediction")
    return prediction


def build_score_frame(
    rows: pd.DataFrame, mhat: ArrayLike, calibration: C3Calibration,
    identity: ModelIdentity, *, require_oos: bool = True,
) -> pd.DataFrame:
    """Attach fresh predictions without aligning a positional vector after sorting."""
    result = canonical_rows(rows, require_order=True)
    values = np.asarray(mhat, dtype=np.float32).reshape(-1)
    if len(values) != len(result) or not np.isfinite(values).all():
        raise ValueError("finite Mhat must match the canonical score population")
    if require_oos:
        earliest = min(_utc(value, "origin") for value in result["origin_id"])
        if earliest <= _utc(calibration.finalized_at_utc, "finalized_at"):
            raise ValueError("OOS forecast origin must follow frozen calibration finalization")
        calibration_year = _utc(calibration.maximum_label_maturity_utc, "maturity").tz_convert("America/New_York").year
        if set(result["year"]) != {calibration_year + 1}:
            raise ValueError("C3 applies to its following-year OOS fold")
    result["Mhat"] = values
    result["S2C-RAW"] = decode_raw(values, calibration.scale)
    result["S2C-C3"] = decode_c3(values, result["category"].tolist(), calibration, identity)
    return canonical_rows(result, require_scores=True, require_order=True)


@dataclass(frozen=True)
class TailThresholds:
    """Strict-event cut points fitted only on a restricted-refit population."""

    p95: float
    p99: float
    rows: int
    sessions: int
    population_sha256: str


def fit_tail_thresholds(restricted_refit_rows: pd.DataFrame) -> TailThresholds:
    rows = canonical_rows(restricted_refit_rows, check_weights=False)
    expected = hierarchy_weights(rows)
    if not np.allclose(rows["weight"].to_numpy(), expected, atol=1e-15, rtol=1e-12):
        raise ValueError("tail thresholds require the complete restricted-refit hierarchy")
    actual = rows["A"].to_numpy(dtype=np.float64)
    digest_rows = rows[["origin_id", "ticker", "A", "weight"]]
    if not isinstance(digest_rows, pd.DataFrame):
        raise TypeError("tail receipt requires a table of named fields")
    digest = _frame_digest(digest_rows)
    return TailThresholds(
        weighted_left_quantile(actual, expected, .95), weighted_left_quantile(actual, expected, .99),
        len(rows), len(set(rows["session_date_et"])), digest,
    )


def _ranks(values: FloatArray, method: str = "average", descending: bool = False) -> FloatArray:
    order = np.argsort(-values if descending else values, kind="stable")
    ranks = np.empty(len(values), dtype=np.float64)
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and values[order[stop]] == values[order[start]]:
            stop += 1
        if method == "average":
            rank = (start + 1 + stop) / 2
        elif method == "min":
            rank = start + 1
        elif method == "max":
            rank = stop
        else:
            raise ValueError("unsupported rank method")
        ranks[order[start:stop]] = rank
        start = stop
    return ranks


def fractional_top4(values: ArrayLike) -> FloatArray:
    """Fractional top-four membership, including boundary and complete ties."""
    array = _vector(values, "rank vector")
    if len(array) != 20:
        raise ValueError("top-four membership requires twenty stock cells")
    low, high = _ranks(array, "min", True), _ranks(array, "max", True)
    return np.clip((5 - low) / (high - low + 1), 0, 1)


def origin_rank_metrics(actual: ArrayLike, predicted: ArrayLike) -> dict[str, float]:
    truth, prediction = _vector(actual, "A"), _vector(predicted, "P")
    if len(truth) != 20 or prediction.shape != truth.shape:
        raise ValueError("rank metrics require matched twenty-stock origins")
    true_rank, pred_rank = _ranks(truth), _ranks(prediction)
    true_rank -= true_rank.mean()
    pred_rank -= pred_rank.mean()
    ic = _ratio(float(np.dot(true_rank, pred_rank)), float(np.linalg.norm(true_rank) * np.linalg.norm(pred_rank)))
    left, right = np.triu_indices(20, k=1)
    actual_sign = np.sign(truth[left] - truth[right])
    predicted_sign = np.sign(prediction[left] - prediction[right])
    untied = actual_sign != 0
    points = (predicted_sign[untied] == actual_sign[untied]).astype(np.float64)
    points[predicted_sign[untied] == 0] = .5
    concordance = float(points.mean()) if len(points) else float("nan")
    return {
        "spearman_ic": ic, "pair_concordance": concordance,
        "tie_rate": float(np.mean(predicted_sign == 0)),
        "constant_rate": float(prediction.max() == prediction.min()),
        "top4_retrieval": float(np.dot(fractional_top4(truth), fractional_top4(prediction)) / 4),
        "bottom4_retrieval": float(np.dot(fractional_top4(-truth), fractional_top4(-prediction)) / 4),
    }


def scalar_metrics(rows: pd.DataFrame, model: str) -> dict[str, float | int]:
    """Conditional reducer retains inherited cell mass and exposes its MSE mass."""
    if rows.empty:
        raise ValueError("empty cohorts must be skipped")
    actual = _vector(rows["A"].to_numpy(), "A", nonnegative=True)
    predicted = _vector(rows[model].to_numpy(), model, nonnegative=True)
    weights = _vector(rows["weight"].to_numpy(), "weight")
    mass = float(weights.sum())
    if mass <= 0 or (weights <= 0).any():
        raise ValueError("cohort must have positive original mass")
    normalized = weights / mass
    error = predicted - actual
    observed, prediction = float(np.dot(normalized, actual)), float(np.dot(normalized, predicted))
    return {
        "rows": len(rows), "origins": len(set(rows["origin_id"])),
        "sessions": len(set(rows["session_date_et"])), "original_mass": mass,
        "observed": observed, "predicted": prediction,
        "bias": float(np.dot(normalized, error)), "mae": float(np.dot(normalized, np.abs(error))),
        "mse": float(np.dot(normalized, error * error)), "ratio": _ratio(prediction, observed),
        "loss_contribution": float(np.dot(weights, error * error)),
    }


def equal_year_scalar(
    annual: Sequence[Mapping[str, float | int]], full_annual_mse: Sequence[float],
) -> dict[str, float | int]:
    """Equal-year scalar metrics; ratio and contribution share use mean ratios' parts."""
    if not annual or len(annual) != len(full_annual_mse):
        raise ValueError("annual metrics and full MSE denominators must match")
    result: dict[str, float | int] = {
        key: int(sum(int(row[key]) for row in annual)) for key in ("rows", "origins", "sessions")
    }
    for key in (*SCALAR_FIELDS, "original_mass", "loss_contribution"):
        if key != "ratio":
            result[key] = float(np.mean([row[key] for row in annual]))
    result["ratio"] = _ratio(float(result["predicted"]), float(result["observed"]))
    result["loss_share"] = _ratio(float(result["loss_contribution"]), float(np.mean(full_annual_mse)))
    return result


def _origin_table(rows: pd.DataFrame, model: str) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for origin, group in rows.groupby("origin_id", sort=False):
        record: dict[str, object] = {
            "origin_id": origin, "session_date_et": group["session_date_et"].iloc[0],
            "category": group["category"].iloc[0], "slot": group["slot"].iloc[0],
        }
        if "early_close" in group:
            record["early_close"] = bool(group["early_close"].iloc[0])
        record.update(origin_rank_metrics(group["A"].to_numpy(), group[model].to_numpy()))
        records.append(record)
    return pd.DataFrame.from_records(records)


def _rank_annual(origins: pd.DataFrame) -> dict[str, float | int]:
    daily = origins.groupby("session_date_et", sort=True)[list(RANK_FIELDS)].mean()
    if not isinstance(daily, pd.DataFrame):
        raise TypeError("multiple rank fields must reduce to a dataframe")
    result: dict[str, float | int] = {
        "origins": len(origins), "sessions": len(daily),
        "valid_ic_origins": int(origins["spearman_ic"].notna().to_numpy(dtype=bool).sum()),
        "valid_ic_sessions": int(daily["spearman_ic"].notna().to_numpy(dtype=bool).sum()),
        "valid_concordance_origins": int(origins["pair_concordance"].notna().to_numpy(dtype=bool).sum()),
        "valid_concordance_sessions": int(daily["pair_concordance"].notna().to_numpy(dtype=bool).sum()),
    }
    for field in RANK_FIELDS:
        result[field] = _mean_valid(daily[field].to_numpy())
    return result


def _event_arrays(rows: pd.DataFrame, model: str) -> tuple[FloatArray, FloatArray]:
    top = np.empty(len(rows), dtype=np.float64)
    rank = np.empty(len(rows), dtype=np.float64)
    # Integer positions avoid reliance on external dataframe index labels.
    local = rows.reset_index(drop=True)
    for positions in local.groupby("origin_id", sort=False).indices.values():
        values = local.iloc[positions][model].to_numpy(dtype=np.float64)
        top[positions] = fractional_top4(values)
        rank[positions] = _ranks(values)
    return top, rank


def tail_event_metrics(
    rows: pd.DataFrame, model: str, threshold: float, *, scope: str = "ALL",
) -> dict[str, float | int]:
    """Events are strict; false-low is average ascending rank <=10.5."""
    if scope not in ("ALL", *CATEGORIES) or not math.isfinite(threshold):
        raise ValueError("invalid event scope or threshold")
    top, rank = _event_arrays(rows, model)
    base = np.ones(len(rows), dtype=bool) if scope == "ALL" else rows["category"].to_numpy() == scope
    if not base.any():
        raise ValueError("empty event scope must be skipped")
    weights = rows["weight"].to_numpy(dtype=np.float64)
    event = base & (rows["A"].to_numpy(dtype=np.float64) > threshold)
    event_mass = float(weights[event].sum())
    base_mass = float(weights[base].sum())
    captured = float(np.dot(weights[event], top[event]))
    return {
        "threshold": threshold, "rows": int(base.sum()), "event_rows": int(event.sum()),
        "sessions": int(rows.loc[base, "session_date_et"].nunique()),
        "event_mass": event_mass, "base_mass": base_mass,
        "prevalence": _ratio(event_mass, base_mass),
        "top4_recall": _ratio(captured, event_mass),
        "top4_precision": _ratio(captured, float(np.dot(weights[base], top[base]))),
        "false_low_rank": _ratio(float(weights[event & (rank <= 10.5)].sum()), event_mass),
    }


def signed_diagnostics(rows: pd.DataFrame, *, stock: str | None = None) -> pd.DataFrame:
    """Signed auxiliary head diagnostics, using original OOS weights on support."""
    required = {"aux_supported", *[f"R_{part}" for part in SIGNED_COMPONENTS], *[f"Rhat_{part}" for part in SIGNED_COMPONENTS]}
    if not required.issubset(rows.columns):
        raise ValueError("signed diagnostics require supported triples and all three signed predictions")
    if not rows["aux_supported"].isin([True, False]).to_numpy(dtype=bool).all():
        raise ValueError("aux_supported must be boolean")
    selected = rows["aux_supported"].to_numpy(dtype=bool).copy()
    if stock is not None:
        if stock not in STOCKS:
            raise ValueError("unknown diagnostic stock")
        selected &= rows["ticker"].to_numpy() == stock
    subset = rows.loc[selected]
    if subset.empty:
        return pd.DataFrame()
    if not subset["category"].eq("OVERNIGHT").all():
        raise ValueError("intraday stock cells cannot have supported auxiliary triples")
    weights = subset["weight"].to_numpy(dtype=np.float64, copy=True)
    weights /= weights.sum()
    records: list[dict[str, object]] = []
    for part in SIGNED_COMPONENTS:
        actual = _vector(subset[f"R_{part}"].to_numpy(), f"R_{part}")
        predicted = _vector(subset[f"Rhat_{part}"].to_numpy(), f"Rhat_{part}")
        observed_mean = float(np.dot(weights, actual))
        predicted_mean = float(np.dot(weights, predicted))
        actual_centered, predicted_centered = actual - observed_mean, predicted - predicted_mean
        covariance = float(np.dot(weights, actual_centered * predicted_centered))
        denominator = float(np.sqrt(np.dot(weights, actual_centered ** 2) * np.dot(weights, predicted_centered ** 2)))
        records.append({
            "stock": stock or "ALL", "component": part, "rows": len(subset),
            "sessions": int(subset["session_date_et"].nunique()),
            "observed": observed_mean, "predicted": predicted_mean,
            "mse": float(np.dot(weights, (predicted - actual) ** 2)),
            "mae": float(np.dot(weights, np.abs(predicted - actual))),
            "covariance": covariance, "pearson": covariance / denominator if denominator > 0 else None,
        })
    return pd.DataFrame.from_records(records)


@dataclass(frozen=True)
class EvaluationTables:
    scalars: pd.DataFrame
    ranks: pd.DataFrame
    events: pd.DataFrame
    signed: pd.DataFrame
    clamping: pd.DataFrame
    pending: tuple[str, ...] = (
        "C0 deciles require a separately authorized independent C0 implementation.",
        "Comparator differences and paired intervals require independent comparator predictions.",
    )


def _cohorts(rows: pd.DataFrame, thresholds: TailThresholds) -> list[tuple[str, str, NDArray[np.bool_]]]:
    cohorts = [("all", "ALL", np.ones(len(rows), dtype=bool))]
    for column, dimension in (("category", "category"), ("slot", "slot"), ("ticker", "stock"), ("early_close", "calendar")):
        for value in rows[column].drop_duplicates():
            label = ("EARLY_CLOSE" if bool(value) else "REGULAR") if column == "early_close" else str(value)
            cohorts.append((dimension, label, rows[column].to_numpy() == value))
    for name, threshold in (("p95", thresholds.p95), ("p99", thresholds.p99)):
        event = rows["A"].to_numpy(dtype=np.float64) > threshold
        for scope in ("ALL", *CATEGORIES):
            base = np.ones(len(rows), dtype=bool) if scope == "ALL" else rows["category"].to_numpy() == scope
            cohorts.append(("tail", f"{scope}:{name}:event", base & event))
            cohorts.append(("tail", f"{scope}:{name}:complement", base & ~event))
    return cohorts


def evaluate_scores(
    scores: pd.DataFrame, thresholds_by_year: Mapping[int, TailThresholds], *,
    expected_years: Sequence[int] = (2021, 2022, 2023, 2024),
) -> EvaluationTables:
    """Recompute annual and equal-year reports from frozen independent scores."""
    rows = canonical_rows(scores, require_scores=True)
    if "early_close" not in rows:
        raise ValueError("full evaluation requires schedule-supplied early_close metadata")
    years = tuple(int(year) for year in expected_years)
    if len(set(years)) != len(years) or set(rows["year"]) != set(years):
        raise ValueError("score years must match the explicitly declared fold years")
    if set(thresholds_by_year) != set(years):
        raise ValueError("each OOS year needs its own restricted-refit tail thresholds")
    scalar_records: list[dict[str, object]] = []
    rank_records: list[dict[str, object]] = []
    event_records: list[dict[str, object]] = []
    signed_frames: list[pd.DataFrame] = []
    clamp_records: list[dict[str, object]] = []
    full_mse: dict[tuple[int, str], float] = {}
    for year in years:
        annual = rows.loc[rows["year"] == year].reset_index(drop=True)
        thresholds = thresholds_by_year[year]
        for model in MODELS:
            full_mse[(year, model)] = float(scalar_metrics(annual, model)["mse"])
            for dimension, group, mask in _cohorts(annual, thresholds):
                if not mask.any():
                    continue
                metrics = scalar_metrics(annual.loc[mask], model)
                metrics["loss_share"] = _ratio(float(metrics["loss_contribution"]), full_mse[(year, model)])
                scalar_records.append({"year": str(year), "model": model, "dimension": dimension, "group": group, **metrics})
            origin_table = _origin_table(annual, model)
            scopes = [("all", "ALL", np.ones(len(origin_table), dtype=bool))]
            for column, dimension in (("category", "category"), ("slot", "slot"), ("early_close", "calendar")):
                for value in origin_table[column].drop_duplicates():
                    group = ("EARLY_CLOSE" if bool(value) else "REGULAR") if column == "early_close" else str(value)
                    scopes.append((dimension, group, origin_table[column].to_numpy() == value))
            for dimension, group, mask in scopes:
                rank_records.append({"year": str(year), "model": model, "dimension": dimension, "group": group, **_rank_annual(origin_table.loc[mask])})
            for name, threshold in (("p95", thresholds.p95), ("p99", thresholds.p99)):
                for scope in ("ALL", *CATEGORIES):
                    if scope != "ALL" and not annual["category"].eq(scope).any():
                        continue
                    event_records.append({"year": str(year), "model": model, "quantile": name, "scope": scope, **tail_event_metrics(annual, model, threshold, scope=scope)})
        for origin, group in annual.groupby("origin_id", sort=False):
            raw, c3, mhat = (group[name].to_numpy(dtype=np.float64) for name in ("S2C-RAW", "S2C-C3", "Mhat"))
            left, right = np.triu_indices(20, 1)
            mhat_ties = mhat[left] == mhat[right]
            for model, values in (("S2C-RAW", raw), ("S2C-C3", c3)):
                clamp_records.append({
                    "year": str(year), "origin_id": origin, "model": model,
                    "category": group["category"].iloc[0], "zero_predictions": int(np.sum(values == 0)),
                    "tied_pairs": int(np.sum(values[left] == values[right])),
                    "new_ties_vs_mhat": int(np.sum((values[left] == values[right]) & ~mhat_ties)),
                })
        if "aux_supported" in annual:
            for stock in (None, *STOCKS):
                diagnostic = signed_diagnostics(annual, stock=stock)
                if not diagnostic.empty:
                    diagnostic.insert(0, "year", str(year))
                    signed_frames.append(diagnostic)
    # EQ conditional metrics exist only if the cohort exists in every fold.
    scalar_frame = pd.DataFrame.from_records(scalar_records)
    for key, subset in scalar_frame.groupby(["model", "dimension", "group"], sort=True):
        if not isinstance(key, tuple) or len(key) != 3:
            raise TypeError("scalar grouping must yield three key fields")
        model, dimension, group = (str(value) for value in key)
        if set(subset["year"]) == {str(year) for year in years}:
            annual_metrics = [{str(key): float(value) for key, value in record.items() if key not in ("year", "model", "dimension", "group")} for record in subset.to_dict(orient="records")]
            equal = equal_year_scalar(annual_metrics, [full_mse[(year, str(model))] for year in years])
            scalar_records.append({"year": "EQ", "model": model, "dimension": dimension, "group": group, **equal})
    rank_frame = pd.DataFrame.from_records(rank_records)
    for key, subset in rank_frame.groupby(["model", "dimension", "group"], sort=True):
        if not isinstance(key, tuple) or len(key) != 3:
            raise TypeError("rank grouping must yield three key fields")
        model, dimension, group = (str(value) for value in key)
        if set(subset["year"]) == {str(year) for year in years}:
            equal_rank: dict[str, object] = {"year": "EQ", "model": model, "dimension": dimension, "group": group}
            for field in RANK_FIELDS:
                equal_rank[field] = _mean_valid(subset[field].to_numpy())
            for field in ("origins", "sessions", "valid_ic_origins", "valid_ic_sessions", "valid_concordance_origins", "valid_concordance_sessions"):
                equal_rank[field] = int(subset[field].to_numpy(dtype=np.int64).sum())
            rank_records.append(equal_rank)
    event_frame = pd.DataFrame.from_records(event_records)
    for key, subset in event_frame.groupby(["model", "quantile", "scope"], sort=True):
        if not isinstance(key, tuple) or len(key) != 3:
            raise TypeError("event grouping must yield three key fields")
        model, quantile, scope = (str(value) for value in key)
        if set(subset["year"]) == {str(year) for year in years}:
            event_equal: dict[str, object] = {"year": "EQ", "model": model, "quantile": quantile, "scope": scope, "threshold": None}
            for field in EVENT_FIELDS:
                event_equal[field] = float(np.mean(subset[field].to_numpy(dtype=np.float64)))
            for field in ("rows", "event_rows", "sessions"):
                event_equal[field] = int(subset[field].to_numpy(dtype=np.int64).sum())
            for field in ("event_mass", "base_mass"):
                event_equal[field] = float(subset[field].to_numpy(dtype=np.float64).mean())
            event_records.append(event_equal)
    signed_frame = pd.concat(signed_frames, ignore_index=True) if signed_frames else pd.DataFrame()
    if not signed_frame.empty:
        eq_signed: list[dict[str, object]] = []
        for key, subset in signed_frame.groupby(["stock", "component"], sort=True):
            if not isinstance(key, tuple) or len(key) != 2:
                raise TypeError("signed grouping must yield two key fields")
            stock, component = (str(value) for value in key)
            if set(subset["year"]) == {str(year) for year in years}:
                record: dict[str, object] = {"year": "EQ", "stock": stock, "component": component}
                for field in ("rows", "sessions"):
                    record[field] = int(subset[field].to_numpy(dtype=np.int64).sum())
                for field in ("observed", "predicted", "mse", "mae", "covariance", "pearson"):
                    record[field] = float(np.mean(subset[field].to_numpy(dtype=np.float64)))
                eq_signed.append(record)
        signed_frame = pd.concat([signed_frame, pd.DataFrame.from_records(eq_signed)], ignore_index=True)
    return EvaluationTables(pd.DataFrame.from_records(scalar_records), pd.DataFrame.from_records(rank_records), pd.DataFrame.from_records(event_records), signed_frame, pd.DataFrame.from_records(clamp_records))


def align_scores_by_full_key(left: pd.DataFrame, right: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Canonicalize shuffled storage and require full key, label and weight identity."""
    lhs, rhs = canonical_rows(left, require_scores=True), canonical_rows(right, require_scores=True)
    if len(lhs) != len(rhs):
        raise ValueError("score populations differ in size")
    for field in (*KEY_FIELDS, "A", "weight"):
        if not lhs[field].equals(rhs[field]):
            raise ValueError(f"full-key comparison mismatch: {field}")
    if "early_close" in lhs or "early_close" in rhs:
        if "early_close" not in lhs or "early_close" not in rhs or not lhs["early_close"].equals(rhs["early_close"]):
            raise ValueError("calendar metadata mismatch")
    return lhs, rhs


def _jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        number = float(value)
        # JSON null records an undefined diagnostic; never silently replace by 0.
        return number if math.isfinite(number) else None
    return value


def _write_json(path: Path, contents: object) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(_jsonable(contents), handle, indent=2, allow_nan=False)
        handle.write("\n")


def write_score_bundle(
    destination: Path, scores: pd.DataFrame, calibrations_by_year: Mapping[int, C3Calibration],
    thresholds_by_year: Mapping[int, TailThresholds], *, run_id: str,
) -> Path:
    """Create a new independent-score bundle; no old file can be overwritten."""
    if not run_id or destination.exists():
        raise ValueError("a new destination and nonempty independent run_id are required")
    rows = canonical_rows(scores, require_scores=True, require_order=True)
    years = tuple(sorted(int(year) for year in rows["year"].unique()))
    if set(calibrations_by_year) != set(years) or set(thresholds_by_year) != set(years):
        raise ValueError("score bundle needs calibration and refit threshold receipt for each year")
    for year in years:
        calibration = calibrations_by_year[year]
        annual = rows.loc[rows["year"] == year]
        regenerated = build_score_frame(annual, annual["Mhat"].to_numpy(), calibration, calibration.identity)
        if not np.array_equal(regenerated[list(MODELS)].to_numpy(), annual[list(MODELS)].to_numpy()):
            raise ValueError("stored magnitudes do not equal frozen C3/RAW decoding")
    destination.mkdir(parents=True, exist_ok=False)
    score_path = destination / "scores.parquet"
    rows.to_parquet(score_path, index=False)
    manifest = {
        "format": "independent-s2c-phase2-scores-v1", "run_id": run_id,
        "producer": "evaluation.py from EXPERIMENT_SPEC.md; no archival/comparator inputs",
        "score_file": "scores.parquet", "score_sha256": sha256(score_path.read_bytes()).hexdigest(),
        "years": list(years), "rows": len(rows), "stock_order": list(STOCKS),
        "calibrations": {str(year): asdict(calibrations_by_year[year]) for year in years},
        "tail_thresholds": {str(year): asdict(thresholds_by_year[year]) for year in years},
        "undefined_json_diagnostics": "null; tabular undefined metrics retain NaN/inf",
    }
    _write_json(destination / "manifest.json", manifest)
    return destination / "manifest.json"


def _calibration_from_dict(value: dict[str, object]) -> C3Calibration:
    identity_value = value["identity"]
    category_values = value["categories"]
    contribution_values = value["contributions"]
    if not isinstance(identity_value, dict) or not isinstance(category_values, list) or not isinstance(contribution_values, dict):
        raise ValueError("invalid frozen calibration receipt")
    identity = ModelIdentity(str(identity_value["recipe_sha256"]), str(identity_value["checkpoint_sha256"]))
    groups: list[CategoryCalibration] = []
    for group in category_values:
        if not isinstance(group, dict) or not isinstance(group["contributions"], dict):
            raise ValueError("invalid group calibration receipt")
        diagnostic = group["contributions"]
        groups.append(CategoryCalibration(
            str(group["category"]), float(group["moment"]), float(group["effective_sessions"]),
            float(group["rho"]), float(group["factor"]), int(group["sessions"]), float(group["original_mass"]),
            ContributionDiagnostic(int(diagnostic["rows"]), float(diagnostic["q_max"]), float(diagnostic["top10_share"]), float(diagnostic["top1pct_share"])),
        ))
    return C3Calibration(
        float(str(value["scale"])), float(str(value["global_moment"])), tuple(groups), identity,
        str(value["role_cutoff_utc"]), str(value["finalized_at_utc"]), str(value["maximum_label_maturity_utc"]),
        str(value["population_sha256"]), ContributionDiagnostic(
            int(contribution_values["rows"]), float(contribution_values["q_max"]),
            float(contribution_values["top10_share"]), float(contribution_values["top1pct_share"]),
        ), float(str(value["kappa"])),
    )


def read_score_bundle(
    manifest_path: Path,
) -> tuple[pd.DataFrame, dict[int, C3Calibration], dict[int, TailThresholds]]:
    """Read only the self-contained new-score format and verify immutable storage."""
    with manifest_path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    if manifest.get("format") != "independent-s2c-phase2-scores-v1" or manifest.get("score_file") != "scores.parquet":
        raise ValueError("not a newly produced independent Phase 2 score bundle")
    score_path = manifest_path.parent / "scores.parquet"
    if sha256(score_path.read_bytes()).hexdigest() != manifest["score_sha256"]:
        raise ValueError("score file digest mismatch")
    if manifest["stock_order"] != list(STOCKS):
        raise ValueError("stored universe/order mismatch")
    rows = canonical_rows(pd.read_parquet(score_path), require_scores=True, require_order=True)
    if len(rows) != manifest["rows"] or set(rows["year"]) != set(manifest["years"]):
        raise ValueError("score receipt population mismatch")
    calibrations = {int(year): _calibration_from_dict(value) for year, value in manifest["calibrations"].items()}
    thresholds = {int(year): TailThresholds(**value) for year, value in manifest["tail_thresholds"].items()}
    for year, calibration in calibrations.items():
        annual = rows.loc[rows["year"] == year]
        predicted = build_score_frame(annual, annual["Mhat"].to_numpy(), calibration, calibration.identity)
        if not np.array_equal(predicted[list(MODELS)].to_numpy(), annual[list(MODELS)].to_numpy()):
            raise ValueError("reloaded predictions do not match frozen calibration")
    return rows, calibrations, thresholds


def report_only_replay(manifest_path: Path, destination: Path) -> EvaluationTables:
    """Rebuild reports from NEW saved scores without training or calibration fitting."""
    rows, _, thresholds = read_score_bundle(manifest_path)
    result = evaluate_scores(rows, thresholds, expected_years=tuple(sorted(thresholds)))
    if destination.exists():
        raise ValueError("report replay requires a fresh output directory")
    destination.mkdir(parents=True, exist_ok=False)
    for name in ("scalars", "ranks", "events", "signed", "clamping"):
        table = getattr(result, name)
        table.to_csv(destination / f"{name}.csv", index=False)
    _write_json(destination / "replay_receipt.json", {
        "source_manifest_sha256": sha256(manifest_path.read_bytes()).hexdigest(),
        "score_sha256": sha256((manifest_path.parent / "scores.parquet").read_bytes()).hexdigest(),
        "operation": "report-only replay from independent Phase 2 scores",
        "fit_calls": 0, "pending": result.pending,
        "undefined_metrics": "NaN/inf in CSV; no replacement with zero",
    })
    return result
