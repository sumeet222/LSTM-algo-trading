"""Read-only P021B transformed-objective attribution and exact private candle reports."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.visualization.hf1m_long import LongStudy

RUN = "HF1M-LONG-TM0-T2-S42-DEV1"
TICKERS = ("AAPL", "AMZN", "TSLA", "SBUX")


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def md(f: pd.DataFrame) -> str:
    def cell(v: object) -> str:
        if isinstance(v, float):
            return repr(v) if np.isfinite(v) else "MISSING/UNTRUSTED"
        return str(v).replace("|", "/")

    return (
        "| "
        + " | ".join(map(str, f.columns))
        + " |\n|"
        + "|".join(["---"] * len(f.columns))
        + "|\n"
        + "\n".join(
            "| " + " | ".join(cell(v) for v in row) + " |"
            for row in f.itertuples(index=False, name=None)
        )
        + "\n"
    )


def analyze(out: Path) -> None:
    root = Path.cwd()
    if out.exists():
        raise ValueError("Use a new output directory; no overwrite")
    s = LongStudy.discover(root)
    # Snapshot prior artifacts, source manifests, registry and checkpoint bytes.
    previous = (
        root
        / Path(
            json.loads((root / "configs/track_a_hf1m_long_visualization_v1.json").read_text())[
                "plan"
            ]["path"]
        ).parent
    )
    protected = [x for x in previous.rglob("*") if x.is_file()]
    protected += [
        root / "configs/CURRENT_EXPERIMENT_REGISTRY.json",
        root / "reports/audit/track_a_real_pairs_v9.jsonl",
        root / "UNRESOLVED_MARKET_DATA_ANOMALIES.md",
    ]
    protected += [root / r["path"] for r in s.plan["protected_refs"]]
    result = s.run_result(RUN)
    protected += [root / r["path"] for r in result["artifacts"].values()]
    before = {str(x): digest(x) for x in protected}
    f = s.prediction(RUN, "refit").copy()
    t = s.targets("refit")
    assert (
        len(f) == 104200 and f.origin_id.nunique() == 5210 and f.session_date_et.nunique() == 2980
    )
    assert not f.duplicated(["ticker", "origin_id"]).any()
    assert f.groupby("origin_id").ticker.apply(lambda v: set(v) == set(SYMBOLS)).all()
    assert f.session_date_et.max() < "2026-01-01" and f.fit_version.eq("refit").all()
    assert result["refit_epochs"] == 7
    recipe = s.recipe("refit")
    scale = float(recipe["t2_scale"])
    eps = float(recipe["epsilon"])
    assert scale == 0.9057319697455458 and f.inverse_count.eq(1).all()
    checkpoint = result["refit"]["checkpoint"]
    assert digest(root / checkpoint["path"]) == checkpoint["sha256"]
    assert f.checkpoint_sha256.eq(checkpoint["sha256"]).all()
    np.testing.assert_allclose(
        scale * np.sinh(f.raw_net_output), f.pred_original_TG20, rtol=2e-7, atol=2e-8
    )
    f = f.merge(
        t[
            [
                "origin_id",
                "ticker",
                "large_numerator",
                "small_mad",
                "tail_class",
                "numerator_p95_train",
                "mad_p05_train",
                "price_proxy_minute_count",
                "assumed_zero_minute_count",
                "poor_volume_hour_count",
                "refit_feature_fallback_cells",
            ]
        ],
        on=["origin_id", "ticker"],
        validate="one_to_one",
    )
    expected = t.set_index(["origin_id", "ticker"]).TG20
    actual = f.set_index(["origin_id", "ticker"]).TG20
    np.testing.assert_array_equal(actual.to_numpy(), expected.reindex(actual.index).to_numpy())
    f["w"] = 1 / (2980 * f.groupby("session_date_et").origin_id.transform("nunique") * 20)
    f["stock_order"] = f.ticker.map({v: i for i, v in enumerate(SYMBOLS)})
    f["z"] = np.arcsinh(f.TG20.to_numpy(dtype=np.float64) / scale)
    np.testing.assert_allclose(f.z, f.T2_z, rtol=1e-13, atol=1e-13)
    f["residual"] = f.z - f.raw_net_output.astype(np.float64)
    f["loss"] = f.residual**2
    f["wl"] = f.w * f.loss
    f["original_scale_loss_context"] = (f.TG20 - f.pred_original_TG20) ** 2
    assert np.isfinite(f.loss).all() and f.loss.ge(0).all()
    np.testing.assert_allclose(f.groupby("session_date_et").w.sum(), 1 / 2980, rtol=1e-14)
    np.testing.assert_allclose(f.w.sum(), 1, rtol=1e-14)
    original = float((f.w * f.original_scale_loss_context).sum())
    reference = pd.read_csv(previous / "metrics.csv")
    ref = reference.loc[reference.run_id.eq(RUN) & reference.partition.eq("refit")].iloc[0]
    np.testing.assert_allclose(
        [original, float((f.w * f.TG20**2).sum())], [ref.mse, ref.zero_mse], rtol=1e-13
    )
    weighted = float(f.wl.sum())
    total = float(f.loss.sum())
    independent = float(f.groupby("session_date_et").loss.mean().mean())
    np.testing.assert_allclose(weighted, independent, rtol=1e-14)
    out.mkdir(parents=True)
    (out / ".gitignore").write_text("*\n!.gitignore\n")

    def write_json(name: str, value: dict) -> None:
        (out / name).write_text(json.dumps(value, indent=2, default=str) + "\n")

    preflight = dict(
        status="PASS_IDENTITY",
        NO_FIT=True,
        run_id=RUN,
        checkpoint=checkpoint,
        input_contract=s.plan["input_contract"],
        source_revision=s.plan["source_revision"],
        symbols=list(SYMBOLS),
        partition="refit",
        phase="REFIT_FINAL",
        epochs=7,
        rows=len(f),
        origins=5210,
        sessions=2980,
        start=f.session_date_et.min(),
        stop=f.session_date_et.max(),
        scale=scale,
        epsilon=eps,
        objective="(asinh(TG20/s_refit)-saved_raw_z_output)^2",
        saved_prediction_space="native z, float32 exports",
        prediction=result["artifacts"]["refit_predictions.parquet"],
    )
    write_json("preflight.json", preflight)
    print(json.dumps(preflight, default=str), flush=True)
    write_json(
        "objective_reconciliation.json",
        dict(
            status="PASS_OBJECTIVE_RECONSTRUCTION",
            weighted_transformed_mse=weighted,
            unweighted_transformed_mse=total / len(f),
            weighted_transformed_rmse=np.sqrt(weighted),
            weighted_loss_sum=weighted,
            unweighted_loss_sum=total,
            independent_equal_day_mean=independent,
            original_scale_mse_context=original,
            zero_original_mse_context=float(ref.zero_mse),
            weight_sum=float(f.w.sum()),
            raw_z_saved=True,
            inverse_once_verified=True,
        ),
    )

    def order(field: str, ascending: bool = False) -> pd.Index:
        return f.sort_values(
            [field, "origin_id", "stock_order"], ascending=[ascending, True, True], kind="stable"
        ).index

    f["abs_y"] = f.TG20.abs()
    f["abs_z"] = f.z.abs()
    f["abs_n"] = f.numerator.abs()
    masks = {}
    threshold_info = {}
    cohort_rows = []
    cross = []
    org = f.drop_duplicates("origin_id").sort_values(
        ["cross_section_mad", "origin_id"], kind="stable"
    )
    for pct in (1, 5):
        k = len(f) * pct // 100
        for prefix, field in [
            ("RAW_TG_ABS", "abs_y"),
            ("Z_ABS", "abs_z"),
            ("NUMERATOR_ABS", "abs_n"),
            ("TRANSFORMED_RESIDUAL_SQ", "loss"),
        ]:
            name = f"{prefix}_TOP_{pct}PCT"
            idx = order(field)[:k]
            masks[name] = f.index.isin(idx)
            cutoff = float(f[field].quantile(1 - pct / 100, interpolation="linear"))
            threshold_info[name] = (
                field,
                cutoff,
                ">=",
                f[field].ge(cutoff).to_numpy(),
                float(f.loc[idx, field].min()),
            )
        name = f"MAD_BOTTOM_{pct}PCT_ORIGINS"
        norig = len(org) * pct // 100
        chosen = org.iloc[:norig].origin_id
        masks[name] = f.origin_id.isin(chosen).to_numpy()
        cutoff = float(org.cross_section_mad.quantile(pct / 100, interpolation="linear"))
        threshold_info[name] = (
            "cross_section_mad",
            cutoff,
            "<=",
            f.cross_section_mad.le(cutoff).to_numpy(),
            float(org.iloc[norig - 1].cross_section_mad),
        )
        np.testing.assert_array_equal(
            masks[f"RAW_TG_ABS_TOP_{pct}PCT"], masks[f"Z_ABS_TOP_{pct}PCT"]
        )

    def stats(mask: np.ndarray) -> dict:
        g = f.loc[mask]
        mass = float(g.w.sum())
        sl = float(g.loss.sum())
        sw = float(g.wl.sum())
        n = len(g)
        return dict(
            rows=n,
            origins=g.origin_id.nunique(),
            origin_fraction=g.origin_id.nunique() / 5210,
            observation_pct=100 * n / len(f),
            weight_mass=mass,
            weighted_loss_sum=sw,
            unweighted_loss_sum=sl,
            weighted_loss_share_pct=100 * sw / weighted,
            unweighted_loss_share_pct=100 * sl / total,
            weighted_mse=sw / mass if mass else None,
            unweighted_mse=sl / n if n else None,
            weighted_rmse=np.sqrt(sw / mass) if mass else None,
            unweighted_rmse=np.sqrt(sl / n) if n else None,
            weighted_concentration=(sw / weighted) / mass if mass else None,
            unweighted_concentration=(sl / total) / (n / len(f)) if n else None,
            numerator_signed_min=g.numerator.min(),
            numerator_signed_max=g.numerator.max(),
            numerator_abs_mean=g.abs_n.mean(),
            numerator_abs_median=g.abs_n.median(),
            return_signed_mean=g.return_4h.mean(),
            return_signed_min=g.return_4h.min(),
            return_signed_max=g.return_4h.max(),
            abs_z_min=g.abs_z.min(),
            abs_z_max=g.abs_z.max(),
            abs_z_mean=g.abs_z.mean(),
            abs_z_median=g.abs_z.median(),
            proxy_input_minute_mean=g.price_proxy_minute_count.mean(),
            assumed_zero_input_minute_mean=g.assumed_zero_minute_count.mean(),
            raw_target_top1_overlap=int((mask & masks["RAW_TG_ABS_TOP_1PCT"]).sum()),
            raw_target_top5_overlap=int((mask & masks["RAW_TG_ABS_TOP_5PCT"]).sum()),
            original_scale_loss_share_context_pct=100
            * float((g.w * g.original_scale_loss_context).sum())
            / original,
        )

    oracle_errors = []
    for name, mask in list(masks.items()):
        field, cutoff, op, thresholdmask, boundary = threshold_info[name]
        for definition, m in [
            ("stable_rank_topK", mask),
            ("linear_quantile_threshold", thresholdmask),
        ]:
            for side, mm in [("cohort", m), ("complement", ~m)]:
                rec = dict(
                    cohort=name,
                    definition=definition,
                    side=side,
                    field=field,
                    cutoff=cutoff,
                    operator=op,
                    rank_boundary=boundary,
                    **stats(mm),
                )
                cohort_rows.append(rec)
            np.testing.assert_allclose(
                stats(m)["weighted_loss_share_pct"] + stats(~m)["weighted_loss_share_pct"],
                100,
                atol=1e-12,
            )
        # Independent NumPy summation, separate indices and scalar loss arithmetic.
        ix = np.flatnonzero(mask)
        z = f.z.to_numpy()
        pred = f.raw_net_output.to_numpy()
        w = f.w.to_numpy()
        oracle = float(np.dot(w[ix], np.square(z[ix] - pred[ix])))
        oracle_errors.append(abs(oracle - float(f.loc[mask, "wl"].sum())))
        assert oracle_errors[-1] < 1e-12
    for pct in (1, 5):
        n = masks[f"NUMERATOR_ABS_TOP_{pct}PCT"]
        d = masks[f"MAD_BOTTOM_{pct}PCT_ORIGINS"]
        flags = {
            "BOTH": n & d,
            "LARGE_NUM_ONLY": n & ~d,
            "SMALL_MAD_ONLY": d & ~n,
            "NEITHER": ~(n | d),
        }
        f[f"mechanism_{pct}"] = np.select(
            [flags["BOTH"], flags["LARGE_NUM_ONLY"], flags["SMALL_MAD_ONLY"]],
            ["BOTH", "LARGE_NUM_ONLY", "SMALL_MAD_ONLY"],
            default="NEITHER",
        )
        masks[f"BOTH_{pct}"] = flags["BOTH"]
        masks[f"UNION_{pct}"] = n | d
        for population, pop in [
            ("full", np.ones(len(f), dtype=bool)),
            ("RAW_TOP1", masks["RAW_TG_ABS_TOP_1PCT"]),
            ("RAW_TOP5", masks["RAW_TG_ABS_TOP_5PCT"]),
            ("Z_TOP1", masks["Z_ABS_TOP_1PCT"]),
            ("Z_TOP5", masks["Z_ABS_TOP_5PCT"]),
        ]:
            for cls, mask in flags.items():
                g = pop & mask
                v = stats(g)
                cross.append(
                    dict(
                        percentile=pct,
                        population=population,
                        mechanism=cls,
                        pct_of_population_weighted_loss=100
                        * float(f.loc[g, "wl"].sum())
                        / float(f.loc[pop, "wl"].sum()),
                        pct_of_population_unweighted_loss=100
                        * float(f.loc[g, "loss"].sum())
                        / float(f.loc[pop, "loss"].sum()),
                        **v,
                    )
                )
            assert sum(int((pop & m).sum()) for m in flags.values()) == int(pop.sum())
            np.testing.assert_allclose(
                sum(float(f.loc[pop & m, "wl"].sum()) for m in flags.values()),
                float(f.loc[pop, "wl"].sum()),
                rtol=1e-14,
            )
        for name, mask in [("BOTH", n & d), ("UNION", n | d)]:
            cohort_rows.append(
                dict(
                    cohort=f"{name}_{pct}", definition="set_operation", side="cohort", **stats(mask)
                )
            )
    for prefix in ("RAW_TG_ABS", "Z_ABS", "NUMERATOR_ABS"):
        assert not (masks[f"{prefix}_TOP_1PCT"] & ~masks[f"{prefix}_TOP_5PCT"]).any()
    cohorts = pd.DataFrame(cohort_rows)
    mechanisms = pd.DataFrame(cross)
    cohorts.loc[~cohorts.cohort.str.startswith(("Z_ABS", "TRANSFORMED"))].to_csv(
        out / "section1_raw_target_component_cohorts.csv", index=False
    )
    cohorts.loc[cohorts.cohort.str.startswith("Z_ABS")].to_csv(
        out / "section2_transformed_target_cohorts.csv", index=False
    )
    cohorts.loc[cohorts.cohort.str.startswith("TRANSFORMED")].to_csv(
        out / "section2_transformed_error_rank_sensitivity.csv", index=False
    )
    mechanisms.to_csv(out / "section1_raw_target_mechanism_cross_tabs.csv", index=False)
    f["error_rank"] = 0
    f.loc[order("loss"), "error_rank"] = np.arange(1, len(f) + 1)
    for pct in (1, 5):
        f[f"target{pct}"] = masks[f"RAW_TG_ABS_TOP_{pct}PCT"]
        f[f"num{pct}"] = masks[f"NUMERATOR_ABS_TOP_{pct}PCT"]
        f[f"mad{pct}"] = masks[f"MAD_BOTTOM_{pct}PCT_ORIGINS"]
        f[f"z{pct}"] = masks[f"Z_ABS_TOP_{pct}PCT"]
    # Independent NumPy rank oracle, without pandas sorting or shared rank indices.
    stocks = f.stock_order.to_numpy()
    origins_key = f.origin_id.to_numpy()
    for pct in (1, 5):
        for prefix, field in [
            ("RAW_TG_ABS", "abs_y"),
            ("Z_ABS", "abs_z"),
            ("NUMERATOR_ABS", "abs_n"),
        ]:
            idx = np.lexsort((stocks, origins_key, -f[field].to_numpy()))[: len(f) * pct // 100]
            np.testing.assert_array_equal(
                np.sort(np.flatnonzero(masks[f"{prefix}_TOP_{pct}PCT"])), np.sort(idx)
            )
        unique = f.drop_duplicates("origin_id")
        idx = np.lexsort((unique.origin_id.to_numpy(), unique.cross_section_mad.to_numpy()))[
            : 5210 * pct // 100
        ]
        expected = f.origin_id.isin(unique.iloc[idx].origin_id).to_numpy()
        np.testing.assert_array_equal(expected, masks[f"MAD_BOTTOM_{pct}PCT_ORIGINS"])
    event_records = []
    selected = {}
    for ticker in TICKERS:
        a = f.loc[f.ticker.eq(ticker)].sort_values(
            ["wl", "loss", "origin_id"], ascending=[False, False, True], kind="stable"
        )
        for rank, i in enumerate(a.head(5).index, 1):
            f.at[i, "stock_weighted_loss_rank"] = rank
            selected[i] = ["top5 within ticker by w*(z-z_hat)^2; raw loss then origin ties"]
    assert len(selected) == 20
    origins = s.table("origins").set_index("origin_id")
    grid = s.table("grid")
    q = s.table("candles_quality")
    qindex = q.set_index(["step", "ticker"])
    candles = []
    vectors = []
    checks = []
    sections = {}
    primary = set()
    for ticker in TICKERS:
        primary.add(next(i for i in selected if f.at[i, "ticker"] == ticker))
    candlecols = [
        "hour_start_utc",
        "hour_end_utc",
        "start_et",
        "end_et",
        "open",
        "high",
        "low",
        "close",
        "observed_volume",
        "genuine_count",
        "expected_minutes",
        "missing_count",
        "proxy_count",
        "quarantine_count",
        "conflict_count",
        "assumed_zero_missing_count",
        "volume_for_feature",
        "hourly_volume_lower_bound",
        "price_factor",
        "price_basis_id",
        "volume_basis_id",
        "genuine_close",
        "extrema_complete",
        "context",
        "overnight_break_before",
        "entry_marker",
        "exit_marker",
    ]
    for number, (i, reasons) in enumerate(selected.items(), 1):
        row = f.loc[i]
        o = origins.loc[row.origin_id]
        first = int(o.first_step)
        entry = int(o.entry_index)
        exit_ = int(o.exit_index)
        assert entry - first == 47 and exit_ - entry == 4
        rv = []
        for ticker in SYMBOLS:
            a = qindex.loc[[(entry, ticker)], :].iloc[0]
            b = qindex.loc[[(exit_, ticker)], :].iloc[0]
            assert a.genuine_close and b.genuine_close
            ret = float(np.log(float(b.close) / float(a.close)))
            rv.append(ret)
            vectors.append(
                dict(
                    case_id=number,
                    origin_id=row.origin_id,
                    ticker=ticker,
                    entry_close=a.close,
                    exit_close=b.close,
                    return_4h=ret,
                    entry_price_basis=a.price_basis_id,
                    exit_price_basis=b.price_basis_id,
                )
            )
        med = float(np.median(rv))
        mad = float(np.median(np.abs(np.array(rv) - med)))
        ret = rv[SYMBOLS.index(row.ticker)]
        y = (ret - med) / (mad + eps)
        np.testing.assert_allclose(
            [ret, med, mad, y, np.arcsinh(y / scale)],
            [row.return_4h, row.cross_section_median, row.cross_section_mad, row.TG20, row.T2_z],
            rtol=1e-11,
            atol=1e-12,
        )
        direct_loss = (np.arcsinh(y / scale) - float(row.raw_net_output)) ** 2
        np.testing.assert_allclose(direct_loss, row.loss, rtol=3e-7, atol=1e-9)
        day_origins = origins.loc[
            origins.refit_admitted & origins.session_date_et.eq(row.session_date_et)
        ]
        np.testing.assert_allclose(row.w, 1 / (2980 * len(day_origins) * 20), rtol=1e-14)
        assert o.exit_end_utc > o.issuance_utc and o.issuance_utc > o.entry_end_utc
        start = str(grid.iloc[first].session_date_et)
        end = str(grid.iloc[exit_].session_date_et)
        hist = s.history(row.ticker, start, end).set_index("hour_end_utc")
        hh = grid.iloc[first : exit_ + 1].copy()
        hh["step"] = np.arange(first, exit_ + 1)
        hh = hh.merge(
            hist.reset_index(),
            on=["hour_start_utc", "hour_end_utc", "session_date_et"],
            how="left",
            validate="one_to_one",
        )
        qq = q.loc[q.ticker.eq(row.ticker), ["hour_end_utc", "volume_basis_id"]]
        hh = hh.merge(qq, on="hour_end_utc", how="left", validate="one_to_one")
        assert len(hh) == 52
        assert hh.iloc[47].genuine_close and hh.iloc[-1].genuine_close
        np.testing.assert_allclose(
            [hh.iloc[47].close, hh.iloc[-1].close],
            [
                qindex.loc[[(entry, row.ticker)], :].iloc[0].close,
                qindex.loc[[(exit_, row.ticker)], :].iloc[0].close,
            ],
            rtol=0,
            atol=0,
        )
        hh["start_et"] = pd.to_datetime(hh.hour_start_utc).dt.tz_convert("America/New_York")
        hh["end_et"] = pd.to_datetime(hh.hour_end_utc).dt.tz_convert("America/New_York")
        hh["context"] = np.where(
            hh.step.le(entry), "BEFORE origin / input", "AFTER issuance / outcome"
        )
        hh["overnight_break_before"] = pd.to_datetime(hh.hour_start_utc).gt(
            pd.to_datetime(hh.hour_end_utc).shift()
        )
        hh["entry_marker"] = hh.step.eq(entry)
        hh["exit_marker"] = hh.step.eq(exit_)
        hh["case_id"] = number
        hh["origin_id"] = row.origin_id
        hh["source_offset"] = hh.step - entry
        candles.append(hh)
        event = row.to_dict()
        for legacy in ("error", "squared_error", "abs_error", "zero_squared_error"):
            event["original_TG20_" + legacy + "_CONTEXT"] = event.pop(legacy)
        event.update(
            case_id=number,
            selection="; ".join(reasons),
            entry_close=float(hh.iloc[47].close),
            exit_close=float(hh.iloc[-1].close),
            issuance_utc=str(o.issuance_utc),
            issuance_et=str(o.issuance_utc.tz_convert("America/New_York")),
            maturity_utc=str(o.label_maturity_utc),
            maturity_et=str(o.label_maturity_utc.tz_convert("America/New_York")),
            loss_share_pct=100 * row.loss / total,
            weighted_loss_share_pct=100 * row.wl / weighted,
            loss_percentile=100 * (1 - (row.error_rank - 1) / len(f)),
            candle_locator=f"case-{number}",
            scale=scale,
        )
        event.update(
            origin_utc=str(o.entry_end_utc),
            origin_et=str(o.entry_end_utc.tz_convert("America/New_York")),
            exit_et=str(o.exit_end_utc.tz_convert("America/New_York")),
            entry_source_id=str(hh.iloc[47].hour_id),
            exit_source_id=str(hh.iloc[-1].hour_id),
            entry_price_basis=str(hh.iloc[47].price_basis_id),
            exit_price_basis=str(hh.iloc[-1].price_basis_id),
        )
        event_records.append(event)
        operand = pd.DataFrame({"operand": list(event), "value": list(event.values())})
        sections[i] = (
            f'## Case {number}: {row.ticker} / {row.origin_id}\n<a id="case-{number}"></a>\n\n'
            + md(operand)
            + (
                "\nExact 48 scheduled input hours and four outcome hours (UTC and E"
                "T). Overnight breaks are explicit; stubs are not model steps. Unk"
                "nown/untrusted OHLC remain missing; no interpolation. Observed sh"
                "ares are not split-adjusted; feature volume is a lower bound wher"
                "e marked. Source offsets and all additional provenance fields are"
                " in case_candles.csv.\n\n"
            )
            + md(hh[candlecols])
            + "\nAll20 endpoint returns:\n\n"
            + md(pd.DataFrame([v for v in vectors if v["case_id"] == number]))
        )
        checks.append(
            dict(
                case_id=number,
                ticker=row.ticker,
                origin_id=row.origin_id,
                rows=52,
                median=med,
                mad=mad,
                reconstructed_target=y,
                status="PASS",
                genuine_endpoints=True,
                output_inverse_once=True,
            )
        )
    assert len(checks) == 20
    cf = pd.concat(candles, ignore_index=True)
    assert len(cf) == 1040
    cf.to_csv(out / "top20_exact_hourly_candles.csv", index=False)
    pd.DataFrame(vectors).to_csv(out / "top20_all_stock_forward_returns.csv", index=False)
    ev = pd.DataFrame(event_records, index=list(selected))
    ev["case_id"] = np.arange(1, 21)
    ev["candle_link"] = [f"P021B_T2_S42_TOP20_EXACT_CANDLE_ANNEX.md#case-{i}" for i in range(1, 21)]
    ev.to_csv(out / "top20_loss_events.csv", index=False)
    mainname = "P021B_T2_S42_TRANSFORMED_TRAINING_TAIL_ATTRIBUTION.md"
    annexname = "P021B_T2_S42_TOP20_EXACT_CANDLE_ANNEX.md"
    compact = cohorts.loc[
        cohorts.definition.isin(["stable_rank_topK", "set_operation"]) & cohorts.side.eq("cohort"),
        [
            "cohort",
            "rows",
            "origins",
            "weight_mass",
            "weighted_loss_share_pct",
            "unweighted_loss_share_pct",
            "weighted_mse",
            "unweighted_mse",
        ],
    ]
    executive = f"""# T2 seed42 transformed-objective training-tail
attribution\n\nFinal-checkpoint in-sample weighted transformed MSE **{weighted!r}**,
unweighted transformed MSE **{total / len(f)!r}**, weighted transformed RMSE
**{np.sqrt(weighted)!r}**.\n\n""" + md(compact)
    definitions = r"""
## Identity, weights and objective

Only HF1M-LONG-TM0-T2-S42-DEV1 final fresh refit, 7epochs,104200rows,
5210origins,2980sessions. Source revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56,
P019B adjusted/quarantined → P020 FT16/TG20 → P021. See preflight.json for exact
checkpoint/prediction/input-contract hashes, symbol order and historical date limits.

r=log(genuine_exit/genuine_entry), m=median20(r), n=r-m, D=median20(|r-m|),
y=n/(D+epsilon_refit), z=asinh(y/s_refit), loss_z=(z-saved_raw_z_prediction)^2.
All primary loss sums and shares here are in z-space. Original-scale error columns
are explicitly secondary context. RMSE is not additive.

Weights=1/(2980×eligible_origins_in_session×20); sum=1. Training executor uses
per-session mean over valid origins and20stocks, then equal-session mean per minibatch.
Each epoch visits every session once, shuffled for optimization; final short batch
has fewer sessions, so each optimizer update is a minibatch mean rather than one fixed
whole-epoch weighted gradient. Saved epoch summaries average individual session losses.
This report is fixed final checkpoint, eval mode/dropout disabled, not historical
online pre-update losses with changing weights and dropout active.

Ranks use absolute original numerator n, not absolute stock return r. Stock-row ranks
break ties by origin ID then canonical stock order. MAD ranks5210unique origins by
raw D, ties by origin ID, then expands all20stocks. Bottom1%=floor(52.1)=52origins,
1040rows; bottom5%=floor(260.5)=260origins,5200rows. Linear quantile thresholds and
>=/<= membership counts are separately reported; stable topK defines primary cohorts.
Top1 subsets nest in top5. Complements and four disjoint flags conserve loss exactly.

## Section 1: raw target components, transformed loss

Full precision counts, thresholds, signed numerator/raw-return summaries, |z| moments,
source input proxy/assumed-zero summaries, conditional MSE/RMSE, overlap and complements:
section1_raw_target_component_cohorts.csv. Columns below remain global transformed loss
shares unless explicitly within-cohort. Intersections are never added twice; union
contribution is separately reported. A shared MAD is one origin event, not20 independent
MAD events. Empty intersections have0rows and0loss with undefined conditional MSE.
"""
    distribution = pd.DataFrame(
        [
            dict(q=q, abs_y=float(f.abs_y.quantile(q)), abs_z=float(f.abs_z.quantile(q)))
            for q in (0.5, 0.9, 0.95, 0.99, 0.999, 1)
        ]
    )
    distribution.to_csv(out / "distribution_compression.csv", index=False)
    definitions += "\nRefit constants: s=" + repr(scale) + "; epsilon=" + repr(eps) + ".\n"
    definitions += "\nDistribution compression (absolute magnitudes):\n\n" + md(distribution)
    main = executive + definitions + "\n" + md(mechanisms.loc[mechanisms.population.eq("full")])
    main += "\n### Within original target and transformed target tails\n\n" + md(
        mechanisms.loc[~mechanisms.population.eq("full")]
    )
    main += """\n## Section 2: transformed-target extremes\n\nWith one positive refit scale,
|z|=asinh(|y|/s) is strictly increasing. Exact top1/top5 membership identity was verified;
no new extreme events appear. Cutoffs and distribution compression:\n\n""" + md(
        cohorts.loc[
            cohorts.cohort.str.startswith(("RAW_TG_ABS", "Z_ABS"))
            & cohorts.definition.eq("stable_rank_topK")
            & cohorts.side.eq("cohort")
        ]
    )
    main += """\nError-ranked sensitivity is separate:
section2_transformed_error_rank_sensitivity.csv ranks (z-z_hat)^2, with target-ranked
overlap.\n"""
    main += """\n## Section 3: twenty highest weighted transformed-loss events\n\nExactly5per
ticker, ranked by w*loss_z, then larger loss_z, then earliest origin ID. Global raw-loss
rank distinguishes magnitude from weighting. Each source window has48full scheduled input
positions and4future positions; no closing stub is modeled. Stubs are outside the
model/target.\n\n""" + md(
        ev[
            [
                "case_id",
                "ticker",
                "origin_id",
                "stock_weighted_loss_rank",
                "error_rank",
                "z",
                "raw_net_output",
                "loss",
                "w",
                "wl",
                "mechanism_1",
                "mechanism_5",
                "candle_link",
            ]
        ]
    )
    for i in selected:
        # Main contains all20 detailed operand tables; annex contains every exact candle.
        section = sections[i]
        main += (
            "\n"
            + section.split("Exact 48 scheduled")[0]
            + "\n[Complete exact candles](%s#case-%s)\n" % (annexname, int(ev.loc[i, "case_id"]))
        )
    synthesis = (
        ev.groupby(["mechanism_1", "mechanism_5"])
        .agg(cases=("ticker", "size"), weighted_loss=("wl", "sum"))
        .reset_index()
    )
    main += "\n## Cross-case synthesis and limits\n\n" + md(synthesis)
    for pct in (1, 5):
        full = (
            mechanisms.loc[mechanisms.percentile.eq(pct) & mechanisms.population.eq("full")]
            .sort_values("weighted_loss_share_pct", ascending=False)
            .iloc[0]
        )
        main += f"""\nAt {pct}% thresholds, **{full.mechanism}** contributes most total
transformed loss: {full.weighted_loss_share_pct!r}% weighted,
{full.unweighted_loss_share_pct!r}% unweighted. Contribution, conditional loss
concentration, and target-tail membership are distinct; see each table.\n"""
    limits = """
These are ex-post in-sample explanations, not time-available signals, learnability,
gradient attribution or causal mechanisms. Small MAD magnifies a fixed numerator
algebraically; neither threshold can still produce a high ratio. asinh compresses
magnitudes without changing genuine returns. Exact stored split-adjusted OHLC and
unadjusted reported-share volumes retain source missingness/quarantine/action vintage,
private rights and end+2minute publication assumptions. Observed volume is a lower
bound when marked; assumed-zero counts are feature-only, not observed zero trades.
Missing/untrusted fields are not interpolated. Endpoints are reference closes, not fills.
All20cases reconstruct all20genuine future returns and median/MAD, target,z,loss and
weight; all20windows preserve scheduled positions and overnight breaks. No new training,
checkpoint replacement, download, dashboard change or2026 numerical access. Ledger36/200.
"""
    (out / mainname).write_text(main + limits)
    (out / annexname).write_text(
        "# Twenty exact transformed-loss case windows\n\n"
        + limits
        + "\n\n"
        + "\n\n".join(sections[i] for i in selected)
    )
    (out / "P021B_HUMAN_REVIEW.md").write_text(
        executive
        + f"\n[Full report]({mainname}) · [All20exact candle cases]({annexname})\n"
        + limits
    )
    assert all(digest(Path(k)) == v for k, v in before.items())
    write_json(
        "independent_verification.json",
        dict(
            status="PASS_EXACT_CANDLES",
            checks=checks,
            tail_status="PASS_TAIL_ATTRIBUTION",
            max_numpy_weighted_sum_discrepancy=max(oracle_errors),
            identical_y_z_memberships=True,
            case_count=20,
            candle_rows=1040,
            source_missingness_cases=int(ev.price_proxy_minute_count.gt(0).sum()),
        ),
    )
    write_json(
        "NO_RETRAINING_AND_PROTECTION_RECEIPT.json",
        dict(
            status="PASS_REPORT_COMPLETENESS",
            NO_FIT=True,
            optimizer_steps=0,
            new_pairs=0,
            ledger="36/200",
            protected_numeric_access=False,
            dashboard_changed=False,
            preserved_sha256=before,
            source_revision=s.plan["source_revision"],
        ),
    )
    print(
        json.dumps(
            dict(
                status="PASS_REPORT_COMPLETENESS",
                weighted_z_mse=weighted,
                unweighted_z_mse=total / len(f),
                headline=compact.to_dict("records"),
                out=str(out),
            ),
            default=str,
        ),
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    analyze(parser.parse_args().out.resolve())
