"""P023 exact case extraction, derived from the preserved P022 reader with extra witnesses."""

from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import SYMBOLS
from .objective_screen_attribution import feature_excerpt
from .objective_screen_source import native_arrays
from .visualization.hf1m_long import LongStudy


def exact_cases(
    study: LongStudy,
    view,
    f: pd.DataFrame,
    pairs: pd.DataFrame,
    arm: str,
    recipe: dict,
    destination: Path,
    extra_indices: dict[int, str] | None = None,
) -> dict:
    indices: dict[int, str] = {}
    for ticker in ("AAPL", "AMZN", "TSLA", "SBUX"):
        selected = (
            f.loc[f.ticker.eq(ticker)]
            .sort_values(["total", "origin_id"], ascending=[False, True])
            .head(5)
        )
        indices.update(
            {int(i): "top5 within ticker by actual weighted objective" for i in selected.index}
        )
    indices.update(extra_indices or {})
    origins = view.source.rows.set_index("origin_id")
    quality = study.table("candles_quality")
    qi = quality.set_index(["step", "ticker"])
    arrays = native_arrays(study, view)
    positions = {key: n for n, key in enumerate(view.source.rows.origin_id)}
    candle_frames, feature_frames, vectors, cases = [], [], [], []
    epsilon = float(study.recipe("refit")["epsilon"])
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
