"""P028 deterministic role-balanced source cases, never selected by forecast performance."""

from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import SYMBOLS
from .objective_screen_attribution import feature_excerpt
from .objective_screen_source import native_arrays
from .visualization.hf1m_long import LongStudy


def extract(
    study: LongStudy,
    view,
    f: pd.DataFrame,
    pairs: pd.DataFrame,
    arm: str,
    recipe: dict,
    destination: Path,
    extra_indices: dict[int, str] | None = None,
) -> dict:
    indices = dict(extra_indices or {})
    origins = view.source.rows.set_index("origin_id")
    quality = study.table("candles_quality")
    qi = quality.set_index(["step", "ticker"])
    arrays = native_arrays(study, view)
    positions = {key: n for n, key in enumerate(view.source.rows.origin_id)}
    candle_frames, feature_frames, vectors, cases = [], [], [], []
    epsilon = float(view.source.fit["epsilon"])
    for case, (index, reason) in enumerate(indices.items(), 1):
        row = f.loc[[index]].iloc[0]
        origin = origins.loc[[row.origin_id]].iloc[0]
        first, entry, exit_ = (
            int(origin.first_step),
            int(origin.entry_index),
            int(origin.exit_index),
        )
        assert entry - first == 47 and exit_ - entry == 4
        candles = (
            quality.loc[quality.ticker.eq(row.ticker) & quality.step.between(first, exit_)]
            .sort_values("step")
            .copy()
        )
        assert len(candles) == 52
        candles["case_id"] = case
        candles["context"] = np.where(
            candles.step <= entry, "INPUT_BEFORE_ISSUANCE", "OUTCOME_AFTER_ISSUANCE"
        )
        candle_frames.append(candles)
        returns = []
        for ticker in SYMBOLS:
            a = qi.loc[[(entry, ticker)]].iloc[0]
            b = qi.loc[[(exit_, ticker)]].iloc[0]
            assert a.genuine_close and b.genuine_close
            r = float(np.log(float(b.close) / float(a.close)))
            returns.append(r)
            vectors.append(
                dict(
                    case_id=case,
                    ticker=ticker,
                    entry_close=a.close,
                    exit_close=b.close,
                    return_4h=r,
                )
            )
        median = float(np.median(returns))
        mad = float(np.median(abs(np.asarray(returns) - median)))
        target = (returns[SYMBOLS.index(row.ticker)] - median) / (mad + epsilon)
        np.testing.assert_allclose(
            [target, median, mad],
            [row.TG20, row.cross_section_median, row.cross_section_mad],
            rtol=1e-11,
            atol=1e-12,
        )
        features = feature_excerpt(view, arrays, positions[row.origin_id], row.ticker)
        features["case_id"] = case
        feature_frames.append(features)
        assert float(row.epsilon) == epsilon
        cases.append(
            dict(
                **{str(k): v for k, v in row.to_dict().items()},
                case_id=case,
                selection=reason,
                first_step=first,
                entry_step=entry,
                exit_step=exit_,
                issuance_utc=str(origin.issuance_utc),
                reconstructed_TG20=target,
            )
        )
    for name, frame in [
        ("cases", pd.DataFrame(cases)),
        ("case_candles", pd.concat(candle_frames)),
        ("case_features", pd.concat(feature_frames)),
        ("case_20_returns", pd.DataFrame(vectors)),
    ]:
        frame.to_parquet(destination / (name + ".parquet"), index=False)
    return dict(
        cases=len(cases),
        candles=sum(len(g) for g in candle_frames),
        feature_cells=sum(len(g) for g in feature_frames),
        target_reconstruction="PASS",
    )


def select(
    populations: dict[str, pd.DataFrame], cuts: dict[str, float]
) -> tuple[pd.DataFrame, list[dict]]:
    """Eleven stable-key witnesses per fitting/development role; no scores/losses used."""
    records = []
    coverage = []
    for role in ("refit", "development"):
        f = populations[role].copy()
        order = f.sort_values(["origin_id", "ticker"]).index
        f = f.loc[order]
        used = set()
        # Label magnitudes are allowed for matured-label diagnostics only, never model selection.
        mag = abs(f.TG20)
        mad = f.cross_section_mad
        quality = f.get("quality", pd.Series("UNKNOWN", index=f.index))
        fallback = f.get("fallback_state", pd.Series("UNKNOWN", index=f.index))
        state = f.panel_state2
        hour = (
            pd.to_datetime(f.entry_end_utc, utc=True).dt.tz_convert("America/New_York").dt.hour
            if "entry_end_utc" in f
            else f.origin_id.str.contains("11:30").map({True: 11, False: 10})
        )
        choices = [
            ("slot10", hour.eq(10)),
            ("slot11", hour.eq(11)),
            ("LOW", state.le(cuts["refit"])),
            ("HIGH", state.gt(cuts["refit"])),
            ("normal_target", mag.le(mag.median())),
            ("extreme_target", mag.ge(mag.quantile(0.99))),
            ("small_MAD", mad.le(mad.quantile(0.05))),
            ("quality_flag", quality.eq("FLAGGED")),
            ("fallback", fallback.eq("ANY_PANEL_PREFIX_FALLBACK")),
            (
                "near_cut",
                state.sub(cuts["refit"]).abs().le(state.sub(cuts["refit"]).abs().quantile(0.05)),
            ),
            ("normal_MAD", mad.between(mad.quantile(0.25), mad.quantile(0.75))),
        ]
        for reason, mask in choices:
            eligible = f.loc[mask & ~f.index.isin(used)]
            present = bool(len(eligible))
            if not present:
                eligible = f.loc[~f.index.isin(used)]
            if not len(eligible):
                raise ValueError("P028_DISTINCT_CASES_UNAVAILABLE")
            row = eligible.iloc[0]
            used.add(row.name)
            records.append(
                dict(
                    role=role,
                    index=int(eligible.index.to_numpy(dtype=int)[0]),
                    origin_id=row.origin_id,
                    ticker=row.ticker,
                    case_id=len(records) + 1,
                    selection=reason if present else reason + ":NOT_PRESENT;earliest_unused",
                )
            )
            coverage.append(
                dict(
                    role=role,
                    criterion=reason,
                    status="PRESENT" if present else "NOT_PRESENT_FALLBACK",
                )
            )
    frame = pd.DataFrame(records)
    if len(frame) != 22 or frame.duplicated(["role", "origin_id", "ticker"]).any():
        raise ValueError("P028_22_UNIQUE_CASES")
    return frame, coverage


def collect(
    study, populations: dict[str, pd.DataFrame], get_view, model, recipe: dict, destination: Path
) -> dict:
    from .config import write_json
    from .state_screen_mechanisms import case_trace
    from .state_screen_spec import CUTS, SCIENCE

    selections, coverage = select(populations, CUTS)
    combined = {
        key: []
        for key in (
            "cases",
            "case_candles",
            "case_features",
            "case_20_returns",
            "case_peer_hidden",
            "case_state_history",
            "case_mechanisms",
        )
    }
    for role in ("refit", "development"):
        f = populations[role].copy()
        f["prediction_rank"] = f.groupby("origin_id").pred_original_TG20.rank(
            ascending=False, method="average"
        )
        f["actual_TG20_rank"] = f.groupby("origin_id").TG20.rank(ascending=False, method="average")
        view = get_view(role)
        subset = selections.loc[selections.role.eq(role)]
        folder = destination / ("selected_" + role)
        folder.mkdir()
        extract(
            study,
            view,
            f,
            pd.DataFrame(),
            model.arm,
            recipe,
            folder,
            {int(r["index"]): r["selection"] for r in subset.to_dict("records")},
        )
        local = pd.read_parquet(folder / "cases.parquet")
        mapping = dict(zip(local.case_id, subset.case_id))
        local["case_id"] = local.case_id.map(mapping)
        local["case_role"] = role
        hidden, states, mechanisms = case_trace(model, view, local)
        for key, frame in [
            ("case_peer_hidden", hidden),
            ("case_state_history", states),
            ("case_mechanisms", mechanisms),
        ]:
            combined[key].append(frame)
        combined["cases"].append(local)
        for key in ("case_candles", "case_features", "case_20_returns"):
            a = pd.read_parquet(folder / (key + ".parquet"))
            a["case_id"] = a.case_id.map(mapping)
            combined[key].append(a)
    for key, frames in combined.items():
        pd.concat(frames, ignore_index=True).to_parquet(
            destination / (key + ".parquet"), index=False
        )
    write_json(
        destination / "case_selection_coverage.json",
        dict(
            rule=SCIENCE["cases"],
            coverage=coverage,
            cases=22,
            unique=True,
            performance_used=False,
            selection_keys=selections.to_dict("records"),
        ),
    )
    return dict(
        cases=22,
        candles=1144,
        feature_cells=len(pd.concat(combined["case_features"])),
        target_reconstruction="PASS",
        roles=["refit", "development"],
    )
