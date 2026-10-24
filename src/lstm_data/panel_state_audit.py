"""P028 two authorized panel proxies only; no targets, models, or training."""

from __future__ import annotations

import argparse
import hashlib
import json
import resource
import sys
import time
from datetime import date
from pathlib import Path

import exchange_calendars as xcals
import numpy as np
import pandas as pd

from .config import fingerprint, now, write_json
from .hf1m_ft16_source import COMMON, checked, ref
from .objective_screen_source import prefix_array
from .peer_screen_authority import JOURNAL, POINTER, rows
from .visualization.hf1m_long import LongStudy

ROLES = ("inner_train", "inner_validation", "refit", "development")
CHANNELS = ("mean20_scaled_M1", "median20_scaled_V1")
COLUMNS = [
    "origin_id",
    "session_date_et",
    "first_step",
    "entry_index",
    "entry_end_utc",
    "issuance_utc",
]


def guard(role: str, stop: str) -> str:
    """Reject protected/unknown requests before looking up a numeric artifact."""
    date.fromisoformat(stop)
    if role not in ROLES or stop >= "2026-01-01" or stop < "2011-04-01":
        raise ValueError("P028_PROTECTED_OR_UNKNOWN_SCOPE_BEFORE_IO")
    return "inner" if role.startswith("inner") else "refit"


def construct(panel: np.ndarray) -> np.ndarray:
    """[time,20,2] scaled M1/V1 → [time,2], float64 pooling then float32."""
    if (
        panel.ndim != 3
        or panel.shape[1:] != (20, 2)
        or panel.dtype != np.float32
        or not np.isfinite(panel).all()
    ):
        raise ValueError("P028_FINITE_COMPLETE20_TWO_CHANNELS")
    x = panel.astype(np.float64)
    return np.stack((x[..., 0].mean(1), np.median(x[..., 1], axis=1)), -1).astype(np.float32)


def describe(values: np.ndarray) -> dict:
    a = np.asarray(values, dtype=float).reshape(-1)
    if not len(a) or not np.isfinite(a).all():
        raise ValueError("P028_FINITE_NONEMPTY_DIAGNOSTIC")
    return dict(
        n=len(a),
        mean=float(a.mean()),
        sd=float(a.std()),
        minimum=float(a.min()),
        q01=float(np.quantile(a, 0.01)),
        q25=float(np.quantile(a, 0.25)),
        median=float(np.median(a)),
        q75=float(np.quantile(a, 0.75)),
        q99=float(np.quantile(a, 0.99)),
        maximum=float(a.max()),
    )


def episodes(days: list[str], high: np.ndarray, calendar: list[str]) -> list[dict]:
    """Maximal state runs, broken by missing exchange sessions; never split a run."""
    if len(days) != len(high) or days != sorted(set(days)):
        raise ValueError("P028_SORTED_UNIQUE_DAYS")
    ordinal = {d: i for i, d in enumerate(calendar)}
    result: list[dict] = []
    for day, state in zip(days, high, strict=True):
        index = ordinal[day]
        if result and result[-1]["state"] == bool(state) and result[-1]["last_index"] + 1 == index:
            result[-1].update(last=day, last_index=index, sessions=result[-1]["sessions"] + 1)
        else:
            result.append(
                dict(first=day, last=day, last_index=index, state=bool(state), sessions=1)
            )
    return result


def support(daily: pd.DataFrame, threshold: float, calendar: list[str], role: str) -> dict:
    high = daily[CHANNELS[1]].to_numpy() > threshold
    runs = episodes(daily.session_date_et.tolist(), high, calendar)
    states: dict[str, dict[str, int]] = {}
    result = dict(role=role, threshold=threshold, tie_rule="LOW<=cut; HIGH>cut", states=states)
    for value, label in [(False, "LOW"), (True, "HIGH")]:
        lengths = [r["sessions"] for r in runs if r["state"] == value]
        qualifying = [n for n in lengths if n >= 5]
        states[label] = dict(
            sessions=int((high == value).sum()),
            maximal_runs=len(lengths),
            runs_at_least_five=len(qualifying),
            sessions_in_qualifying_runs=sum(qualifying),
            longest_run=max(lengths, default=0),
        )
    fitting = role in ("inner_train", "refit")
    required_days, required_runs = (50, 5) if fitting else (20, 2)
    result["passes_proposed_support_policy"] = all(
        s["sessions"] >= required_days and s["runs_at_least_five"] >= required_runs
        for s in states.values()
    )
    result["policy_is_approved"] = False
    result["activation_use"] = (
        "DESCRIPTIVE_ONLY_NOT_A12_ACTIVATION"
        if role == "development"
        else "PROPOSED_A12_POLICY_ONLY"
    )
    return result


def audit(out: Path) -> None:
    """Read only historical feature prefixes; no target file is decoded."""
    started = time.monotonic()
    authority = json.loads((out / "preparation_authorization.json").read_text())
    if (
        authority["status"] != "AUTHORIZED_P028_TWO_CHANNEL_PREPARATION_ONLY"
        or authority["neural_training_authorized"]
    ):
        raise ValueError("P028_EXACT_PREPARATION_ONLY_AUTHORITY")
    before = ref(POINTER), ref(JOURNAL)
    if rows()[-1]["global_started_pairs"] != 59:
        raise ValueError("P028_LEDGER59_REQUIRED")
    study = LongStudy.discover(Path.cwd())
    grid = pd.read_parquet(
        checked(study.contract["files"]["grid"]), filters=[("session_date_et", "<=", "2025-12-31")]
    )
    calendar = [
        str(x.date())
        for x in xcals.get_calendar("XNYS", start="2011-01-01", end="2025-12-31").sessions
    ]
    private = Path("artifacts/hf20_hf1m_long_v1") / out.name
    private.mkdir(exist_ok=False)
    (private / ".gitignore").write_text("*\n!.gitignore\n")
    metrics, phases, regime = [], [], []
    evidence = []
    for phase, roles in [("inner", ROLES[:2]), ("refit", ROLES[2:])]:
        role_rows = {}
        for role in roles:
            guard(role, "2025-06-30" if phase == "inner" else "2025-12-31")
            frame = pd.read_parquet(
                checked(study.contract["files"]["origins"]),
                columns=COLUMNS,
                filters=[(role + "_admitted", "=", True), ("session_date_et", "<=", "2025-12-31")],
            )
            if (
                frame.session_date_et.ge("2026-01-01").any()
                or (frame.entry_index - frame.first_step).ne(47).any()
            ):
                raise ValueError("P028_HISTORICAL48_REQUIRED")
            role_rows[role] = frame.reset_index(drop=True)
        stop = max(int(f.entry_index.max()) for f in role_rows.values()) + 1
        recipe = study.recipe(phase)
        fit_indices = np.asarray(recipe["fit_hour_indices"], dtype=int)
        if grid.iloc[fit_indices].session_date_et.gt(recipe["fit_stop_inclusive"]).any():
            raise ValueError("P028_FUTURE_SCALER_FIT")
        components = checked(study.contract["files"]["components"])
        indices = [COMMON.index("M1"), COMMON.index("V1")]
        scaled = prefix_array(components, phase + "_scaled_common", stop)[..., indices]
        native = prefix_array(components, phase + "_native_common", stop)[..., indices]
        fallback = prefix_array(components, phase + "_fallback_common", stop)[..., indices]
        for j, name in enumerate(("M1", "V1")):
            np.testing.assert_array_equal(fallback[..., j], ~np.isfinite(native[..., j]))
            scaler = recipe["scalers"][name]
            rebuilt = (
                (
                    np.where(np.isfinite(native[..., j]), native[..., j], recipe["fallbacks"][name])
                    - scaler["center"]
                )
                / scaler["scale"]
            ).astype(np.float32)
            np.testing.assert_array_equal(rebuilt, scaled[..., j])
        states = construct(scaled)
        np.testing.assert_array_equal(construct(scaled[:, ::-1]), states)
        # Independent sorted-sample midpoint/sum oracle, no labels or learned transforms.
        oracle = np.stack(
            (
                np.sum(scaled[..., 0].astype(float), axis=1) / 20,
                np.sort(scaled[..., 1].astype(float), axis=1)[:, 9:11].mean(1),
            ),
            -1,
        ).astype(np.float32)
        np.testing.assert_array_equal(states, oracle)
        endpoint_frames = {}
        used = np.zeros(stop, dtype=bool)
        for role, f in role_rows.items():
            h = f.first_step.to_numpy(dtype=int)[:, None] + np.arange(48)
            if (h < 0).any() or h.max() >= stop:
                raise ValueError("P028_PREFIX_INDEX")
            used[h] = True
            end = pd.to_datetime(f.entry_end_utc, utc=True)
            issue = pd.to_datetime(f.issuance_utc, utc=True)
            grid_end = pd.to_datetime(grid.hour_end_utc, utc=True)
            np.testing.assert_array_equal(grid_end.iloc[f.entry_index].to_numpy(), end.to_numpy())
            if (issue - end).ne(pd.Timedelta(minutes=2)).any():
                raise ValueError("P028_ORIGINAL_ISSUANCE_CLOCK")
            clocks = grid_end.astype("int64").to_numpy()[h]
            if (clocks > end.astype("int64").to_numpy()[:, None]).any():
                raise ValueError("P028_FUTURE_STATE_STEP")
            window = states[h]
            endpoint = states[f.entry_index.to_numpy(dtype=int)]
            e = f.copy()
            for j, name in enumerate(CHANNELS):
                e[name] = endpoint[:, j]
                metrics.append(
                    dict(
                        role=role,
                        channel=name,
                        sample="window_occurrences",
                        **describe(window[..., j]),
                    )
                )
                metrics.append(
                    dict(role=role, channel=name, sample="endpoints", **describe(endpoint[:, j]))
                )
            endpoint_frames[role] = e
            filename = private / (role + "_endpoints.parquet")
            e.to_parquet(filename, index=False)
            evidence.append(ref(filename))
            # Endpoints and within-window variation describe source/state, never labels.
            pool = scaled[f.entry_index.to_numpy(dtype=int)]
            inclusive = pool.mean(1, dtype=np.float64)[:, 0]
            loo_mean = (pool[..., 0].sum(1, dtype=float)[:, None] - pool[..., 0]) / 19
            median_loo = np.stack(
                [
                    np.median(np.delete(pool[..., 1], i, axis=1).astype(float), axis=1)
                    for i in range(20)
                ],
                1,
            )
            age = (end.astype("int64").to_numpy()[:, None] - clocks) / 3.6e12
            change = np.std(window.astype(float), axis=1)
            metrics.append(
                dict(
                    role=role,
                    channel="M1_mean_self_inclusion",
                    sample="inclusive_minus_leave_one_out",
                    **describe(inclusive[:, None] - loo_mean),
                )
            )
            metrics.append(
                dict(
                    role=role,
                    channel="V1_median_self_inclusion",
                    sample="inclusive_minus_leave_one_out",
                    **describe(endpoint[:, 1:2] - median_loo),
                )
            )
            record = dict(
                role=role,
                phase=phase,
                phase_recipe_fingerprint=fingerprint(recipe),
                source_components=ref(components),
                origins=len(f),
                sessions=f.session_date_et.nunique(),
                stock_rows=len(f) * 20,
                retained_origins=len(f),
                retention=1.0,
                nonfinite_state_cells=int((~np.isfinite(window)).sum()),
                source_publication_verified=False,
                conditional_clock="PASS_UNDER_EXISTING_P020_ASSUMPTION",
                mean_within_window_SD=change.mean(0).tolist(),
                origins_with_nonconstant_window=(change > 0).sum(0).tolist(),
                fallback_source_cells=fallback[h].sum((0, 1, 2)).astype(int).tolist(),
                origins_with_any_source_fallback=fallback[h]
                .any((1, 2))
                .sum(0)
                .astype(int)
                .tolist(),
                historical_age_wall_hours=describe(age),
                slot_counts=end.dt.tz_convert("America/New_York")
                .dt.strftime("%H:%M")
                .value_counts()
                .to_dict(),
                input_population_fingerprint=fingerprint(f[COLUMNS].astype(str).to_dict("records")),
                state_fingerprint=fingerprint(
                    dict(
                        dtype=str(window.dtype),
                        shape=list(window.shape),
                        bytes_sha256=hashlib.sha256(window.tobytes()).hexdigest(),
                    )
                ),
            )
            phases.append(record)
        training_role = "inner_train" if phase == "inner" else "refit"
        daily_train = (
            endpoint_frames[training_role]
            .sort_values("entry_end_utc")
            .drop_duplicates("session_date_et")
            .sort_values("session_date_et")
        )
        cut = float(np.median(daily_train[CHANNELS[1]]))
        for role, e in endpoint_frames.items():
            daily = (
                e.sort_values("entry_end_utc")
                .drop_duplicates("session_date_et")
                .sort_values("session_date_et")
            )
            regime.append(support(daily, cut, calendar, role))
            f = role_rows[role]
            windows = states[f.first_step.to_numpy(dtype=int)[:, None] + np.arange(48)]
            bins = windows[..., 1] > cut
            row = next(x for x in phases if x["role"] == role)
            row["windows_crossing_proposed_volatility_cut"] = int(
                (bins.any(1) & ~bins.all(1)).sum()
            )
            row["mean_adjacent_proposed_regime_transitions"] = float(
                (bins[:, 1:] != bins[:, :-1]).sum(1).mean()
            )
            row["endpoint_minus_first_step"] = [
                describe(windows[:, -1, j] - windows[:, 0, j]) for j in range(2)
            ]
            daily = daily.assign(proposed_HIGH=daily[CHANNELS[1]].gt(cut))
            file = private / (role + "_daily_support.parquet")
            daily.to_parquet(file, index=False)
            evidence.append(ref(file))
        table = grid.iloc[np.flatnonzero(used)].copy()
        table["step"] = np.flatnonzero(used)
        for j, name in enumerate(CHANNELS):
            table[name] = states[used, j]
        file = private / (phase + "_unique_step_state.parquet")
        table.to_parquet(file, index=False)
        evidence.append(ref(file))
        del native, scaled, fallback, states
    pd.DataFrame(metrics).to_csv(out / "state_distribution.csv", index=False)
    write_json(
        out / "market_state_audit.json",
        dict(
            status="PASS_TWO_CHANNEL_PREPARATION_AUDIT",
            at=now(),
            roles=phases,
            proposed_regime_support=regime,
            authorization=ref(out / "preparation_authorization.json"),
            input_contract=study.plan["input_contract"],
            source_revision=study.contract["revision"],
            channels=list(CHANNELS),
            formula=(
                "float64 mean20(M1), sorted central-pair median20(V1), round once "
                "to float32; existing phase-scaled/fallback inputs"
            ),
            self_inclusion=True,
            independent_market_index=False,
            new_scalers_or_floors=False,
            targets_decoded=False,
            numeric_read_limit="2025-12-31",
            protected_numeric_access=False,
            ledger=59,
            neural_starts=0,
            optimizer_updates=0,
            publication_timing_verified=False,
            conditional_clock_only=True,
            cache=evidence,
            fit_cutoffs=dict(inner="2023-01-23", refit="2025-06-30"),
            seconds=time.monotonic() - started,
            peak_rss_bytes=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            * (1 if sys.platform == "darwin" else 1024),
        ),
    )
    if before != (ref(POINTER), ref(JOURNAL)):
        raise ValueError("P028_PREPARATION_CHANGED_LEDGER")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    audit(parser.parse_args().out)
