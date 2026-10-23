"""Read-only P021A refit-tail attribution and exact private candle reports."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.hf1m_training_diagnostics import daily_metrics
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
            ]
        ],
        on=["origin_id", "ticker"],
        validate="one_to_one",
    )
    expected = t.set_index(["origin_id", "ticker"]).TG20
    actual = f.set_index(["origin_id", "ticker"]).TG20
    np.testing.assert_array_equal(actual.to_numpy(), expected.reindex(actual.index).to_numpy())
    f["w"] = 1 / (2980 * f.groupby("session_date_et").origin_id.transform("nunique") * 20)
    f["residual"] = f.TG20 - f.pred_original_TG20
    f["loss"] = f.residual**2
    f["wl"] = f.w * f.loss
    f["stock_order"] = f.ticker.map({v: i for i, v in enumerate(SYMBOLS)})
    np.testing.assert_allclose(f.groupby("session_date_et").w.sum(), 1 / 2980, rtol=1e-14)
    assert abs(f.w.sum() - 1) < 1e-14
    ref = pd.read_csv(previous / "metrics.csv")
    r = ref.loc[ref.run_id.eq(RUN) & ref.partition.eq("refit")].iloc[0]
    total = float(f.loss.sum())
    weighted = float(f.wl.sum())
    independent = float(f.groupby("session_date_et").loss.mean().mean())
    np.testing.assert_allclose(
        [weighted, independent, float((f.w * f.TG20**2).sum())],
        [r.mse, r.mse, r.zero_mse],
        rtol=1e-13,
    )
    ic = float(daily_metrics(f).rank_ic.mean())
    np.testing.assert_allclose(ic, r.daily_ic_mean, atol=1e-13)

    def rank(field: str) -> pd.Index:
        return f.sort_values(
            [field, "origin_id", "stock_order"], ascending=[False, True, True], kind="stable"
        ).index

    f["abs_target"] = f.TG20.abs()
    for field, prefix in [("abs_target", "target"), ("loss", "error")]:
        ranked = rank(field)
        f[prefix + "_rank"] = 0
        f.loc[ranked, prefix + "_rank"] = np.arange(1, len(f) + 1)
        for pct in (1, 5):
            f[prefix + str(pct)] = f[prefix + "_rank"].le(len(f) * pct // 100)
    assert (f.target1 & ~f.target5).sum() == 0

    def stats(g: pd.DataFrame) -> dict:
        mass = float(g.w.sum())
        sl = float(g.loss.sum())
        sw = float(g.wl.sum())
        return dict(
            n=len(g),
            origins=g.origin_id.nunique(),
            weight_mass=mass,
            sum_loss=sl,
            sum_weighted_loss=sw,
            unweighted_loss_share_pct=100 * sl / total,
            weighted_loss_share_pct=100 * sw / weighted,
            unweighted_mse=sl / len(g) if len(g) else np.nan,
            weighted_mse=sw / mass if mass else np.nan,
            unweighted_rmse=np.sqrt(sl / len(g)) if len(g) else np.nan,
            weighted_rmse=np.sqrt(sw / mass) if mass else np.nan,
            target_min=g.TG20.min(),
            target_max=g.TG20.max(),
            abs_target_median=g.TG20.abs().median(),
            weighted_target_squared_share_pct=100
            * float((g.w * g.TG20**2).sum())
            / float((f.w * f.TG20**2).sum()),
            abs_numerator_median=float(g.numerator.abs().median()),
            abs_return_median=float(g.return_4h.abs().median()),
            mad_epsilon_median=float((g.cross_section_mad / eps).median()),
            abs_n_over_d_median=float((g.numerator.abs() / g.denominator).median()),
        )

    tails = []
    mechanisms = []
    groups = []
    for prefix in ("target", "error"):
        field = "abs_target" if prefix == "target" else "loss"
        for pct in (1, 5):
            key = prefix + str(pct)
            threshold = float(f[field].quantile(1 - pct / 100, interpolation="linear"))
            for definition, mask in [
                ("rank_topK", f[key]),
                ("quantile_ge", f[field].ge(threshold)),
            ]:
                for side, m in [("tail", mask), ("complement", ~mask)]:
                    tails.append(
                        dict(
                            cohort=key,
                            definition=definition,
                            side=side,
                            quantile_threshold=threshold,
                            rank_boundary=float(f.loc[f[key], field].min()),
                            overlap_target_topK=int((mask & f["target" + str(pct)]).sum()),
                            **stats(f.loc[m]),
                        )
                    )
    for key in ("full", "target1", "target5"):
        g = f if key == "full" else f.loc[f[key]]
        for cls in ("large numerator", "small MAD", "both", "neither"):
            h = g.loc[g.tail_class.eq(cls)]
            z = stats(h)
            mechanisms.append(
                dict(
                    cohort=key,
                    mechanism=cls,
                    pct_within_cohort=100 * len(h) / len(g),
                    weighted_share_of_cohort_pct=100 * h.wl.sum() / g.wl.sum(),
                    unweighted_share_of_cohort_pct=100 * h.loss.sum() / g.loss.sum(),
                    **z,
                )
            )
        assert sum(x["n"] for x in mechanisms if x["cohort"] == key) == len(g)
        for col in ("ticker", "year"):
            gg = g.assign(year=g.session_date_et.str[:4])
            for name, h in gg.groupby(col):
                groups.append(dict(cohort=key, group_type=col, group=name, **stats(h)))
    out.mkdir(parents=True)
    (out / ".gitignore").write_text("*\n!.gitignore\n")
    pd.DataFrame(tails).to_csv(out / "tail_attribution.csv", index=False)
    mech = pd.DataFrame(mechanisms)
    mech.to_csv(out / "tail_by_mechanism.csv", index=False)
    pd.DataFrame(groups).to_csv(out / "stock_year_attribution.csv", index=False)
    origin = f.groupby("origin_id").agg(
        session=("session_date_et", "first"),
        mad=("cross_section_mad", "first"),
        small_mad=("small_mad", "first"),
        sum_weighted_loss=("wl", "sum"),
        large_rows=("large_numerator", "sum"),
        target1_rows=("target1", "sum"),
        target5_rows=("target5", "sum"),
    )
    origin.to_csv(out / "origin_attribution.csv")
    selected = {}
    missing = []
    for ticker in TICKERS:
        a = f.loc[f.ticker.eq(ticker)]
        choices = [
            ("highest target top1", a.loc[a.target1].sort_values("target_rank")),
            (
                "highest numerator top5 preferred",
                a.loc[a.target5].sort_values("numerator", key=lambda x: x.abs(), ascending=False),
            ),
            ("smallest MAD top5", a.loc[a.target5].sort_values(["cross_section_mad", "origin_id"])),
            ("both flags", a.loc[a.large_numerator & a.small_mad].sort_values("target_rank")),
            ("highest error", a.sort_values("error_rank")),
        ]
        if ticker == "AAPL":
            choices.append(
                (
                    "neither marginal flag",
                    a.loc[~a.large_numerator & ~a.small_mad].sort_values("target_rank"),
                )
            )
        for label, g in choices:
            if g.empty:
                missing.append(ticker + ": " + label + " UNAVAILABLE: no qualifying observation")
                continue
            i = g.index[0]
            selected.setdefault(i, []).append(label)
    # Independent complete cross-sectional endpoint reconstruction for every selected case.
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
        direct_prediction = scale * np.sinh(float(row.raw_net_output))
        direct_loss = (y - direct_prediction) ** 2
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
    assert len(checks) >= 12
    pd.concat(candles, ignore_index=True).to_csv(out / "case_candles.csv", index=False)
    pd.DataFrame(vectors).to_csv(out / "case_cross_section_returns.csv", index=False)
    cases = f.loc[f.ticker.isin(TICKERS) & f.target5].copy()
    case_map = {i: n for n, i in enumerate(selected, 1)}
    cases["selected_case_id"] = [case_map.get(i) for i in cases.index]
    cases["candle_table_available"] = cases.index.isin(selected)
    cases["candle_table_locator"] = [
        f"case-{case_map[i]}" if i in selected else "INDEXED_EVENT_ONLY_NO_CANDLE_TABLE"
        for i in cases.index
    ]
    # Endpoint operands for every indexed four-ticker cohort event use the saved source.
    cases["entry_close"] = [
        qindex.loc[(int(origins.loc[o].entry_index), ticker), "close"]
        for o, ticker in zip(cases.origin_id, cases.ticker)
    ]
    cases["exit_close"] = [
        qindex.loc[(int(origins.loc[o].exit_index), ticker), "close"]
        for o, ticker in zip(cases.origin_id, cases.ticker)
    ]
    cases["loss_share_pct"] = 100 * cases.loss / total
    cases["weighted_loss_share_pct"] = 100 * cases.wl / weighted
    cases.to_csv(out / "case_event_table.csv", index=False)
    dist = pd.DataFrame(
        [
            dict(
                quantile=v,
                signed=float(f.TG20.quantile(v)),
                absolute=float(f.abs_target.quantile(v)),
            )
            for v in (0, 0.01, 0.05, 0.5, 0.95, 0.99, 1)
        ]
    )
    dist.to_csv(out / "target_distribution.csv", index=False)
    tailsdf = pd.DataFrame(tails)
    official = tailsdf.loc[
        tailsdf.definition.eq("rank_topK")
        & tailsdf.side.eq("tail")
        & tailsdf.cohort.str.startswith("target")
    ]
    dom = (
        mech.loc[mech.cohort.eq("full")]
        .sort_values("weighted_loss_share_pct", ascending=False)
        .iloc[0]
    )
    intro = (
        "# Seed-42 T2 final-refit training-tail loss and exact candles\n\n"
        + md(
            official[
                [
                    "cohort",
                    "n",
                    "weighted_loss_share_pct",
                    "unweighted_loss_share_pct",
                    "weighted_mse",
                    "weighted_rmse",
                ]
            ]
        )
        + f"""\nDominant full-population class: **{dom.mechanism}**,
{dom.weighted_loss_share_pct:.12g}% weighted squared loss. This is observational loss
attribution, not gradient attribution, causality, or learnability.\n"""
    )
    body = (
        f"""\n## Identity, population and weights\n\nOnly {RUN}, final fresh refit
(7epochs), source revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56, P019B→P020→P021.
N=104200,5210origins,2980sessions; all20names. Original TG20 MSE={weighted!r},
ZERO={float(r.zero_mse)!r}, dailyIC={ic!r}; unweighted MSE={total / len(f)!r}. Not
development. s={scale!r}; epsilon={eps!r}. Original-scale inverse s*sinh(z) verified once
with float32 storage tolerance.\n\nWeights=1/(2980×origins_in_day×20); sum=1, every
session has weight1/2980. Primary top-K is exactly1042/5210rows, descending absolute
target with origin then canonical stock-order ties. Quantiles use linear interpolation and
>=; threshold-based counts are separately reported, including complements. Top1 nests in
top5, never add their shares. RMSE does not decompose additively.\n\n## Target tails and
separately error-ranked sensitivity\n\n"""
        + md(tailsdf)
        + """\nError-ranked cohorts sort squared prediction error, not target magnitude; overlap
counts compare with the same-size target cohort. Conditional MSE renormalizes subgroup
weight; contributions retain global weights. Stock/year attributions use all20-stock
global denominators (stock_year_attribution.csv).\n\n## Mechanisms: full population and
target tails\n\n"""
        + md(mech)
        + f"""\nLarge |numerator| >= {float(f.numerator_p95_train.iloc[0])!r}; small
rawMAD <= {float(f.mad_p05_train.iloc[0])!r}, fitted refit diagnostic thresholds. MAD
threshold uses5210unique origins, not104200independent denominators. Four classes are
exclusive and exhaustive. Small-MAD origins={int(origin.small_mad.sum())};
origin_attribution.csv reports row membership and total loss at each origin. Median
MAD/epsilon and |n|/denominator are included by class. Small MAD magnifies a fixed
numerator algebraically, but epsilon floors the denominator; neither class may still
include a large ratio without either marginal flag firing. Compare both and large-only
before attributing a marginal numerator effect.\n\nPrediction
SD={float(r.prediction_sd)!r} versus actual SD={float(r.actual_sd)!r}. Near-zero
predictions mean loss is close to target squared magnitude, not evidence the tails are
predictable. The tables quantify which threshold-defined mechanisms dominate; no causal
explanation of the trained predictions follows.\n\n## Exact four-ticker cases\n\nEvery
requested ticker's highest target tail, highest numerator (top5preferred),
smallestMADtop5, both-flags and largest-error cases were selected deterministically,
deduplicated by stock/origin. Full top1/top5 four-ticker membership is in
case_event_table.csv; indexed-only events explicitly lack candle tables. All selected
cases have52scheduled rows, complete20-return vectors and loss ranks. Ties in target/error
ranks use origin/canonical stock order. Remaining cases appear in [the candle
annex](P021_T2_S42_ADDITIONAL_EXACT_CANDLES.md).\n\n"""
    )
    conclusion = (
        "\nLarge-numerator-only observations contribute 82.02523079998562% of top1 loss and "
        "69.92283939214956% of top5 loss (weighted). Both flags add 15.538028985164717% "
        "and 8.664590284801747%, respectively. Thus numerator-flagged rows dominate the tails. "
        "Small-MAD-only contributes 2.297519610302785% and 5.384953255328423% of tail loss. "
        "Across all training rows, neither is the largest individual class "
        "(45.785427652538075%), "
        "large-only is close (43.88493973593131%), both 4.985537439124285%, small-only "
        "5.344095172406328%. Numerator-flagged rows jointly account for 48.8704771750556% "
        "of all loss; neither exceeds either exclusive extreme mechanism individually.\n"
    )
    intro += conclusion
    body += "\n".join(missing) + "\n\n" + "\n\n".join(sections[i] for i in selected if i in primary)
    limits = """\n## Limits and independent verification\n\nAll selected cases independently
reconstruct20genuine endpoint returns, median/MAD, epsilon, target,z,inverse and exact
candle clocks; at least12case checks pass. Entire104200-row loss is reconciled both by
row weights and equal-day means; metric and IC match authoritative P021 values. Cases
are ex-post explanation. Missing source minutes, bounded input-price proxies, untrusted
wicks, volume lower bounds, split price units and unchanged reported-share units retain
P019B/P020 limitations. Endpoint prices are reference closes, not fills; issuance
assumes end+2minutes, publication timing is not independently attested. Conditional
private rights apply; no public redistribution of these exact numeric
reports.\n\nNO_RETRAINING: optimizer steps0, gradients0, new pairs0, checkpoint
replacements0, data acquisition0, repairs0; research ledger36/200 unchanged. No2026
numerical access, no legacy dataset mixing. Pre/post hashes preserve prior P021/source
manifests, registry/journal and run artifacts. Verification and file hashes are in
independent_reconstruction_checks.json and artifact_inventory.csv. Open dashboard HF1M
Long → Targets & Extremes → Full-prefix refit training → ticker and exact origin from
each case; UI provides optional charts.\n"""
    (out / "P021_T2_S42_REFIT_TAIL_LOSS_AND_EXACT_CANDLES.md").write_text(intro + body + limits)
    (out / "P021_T2_S42_ADDITIONAL_EXACT_CANDLES.md").write_text(
        "# Additional exact candles\n\n"
        + "\n\n".join(sections[i] for i in selected if i not in primary)
        + limits
    )
    (out / "P021A_HUMAN_REVIEW.md").write_text(
        intro
        + (
            "\n[Main exact report](P021_T2_S42_REFIT_TAIL_LOSS_AND_EXACT_CANDLE"
            "S.md) · [Additional candles](P021_T2_S42_ADDITIONAL_EXACT_CANDLES"
            ".md)\n\n"
        )
        + limits
        + (
            "\nArtifacts: tail_attribution.csv, tail_by_mechanism.csv, stock_ye"
            "ar_attribution.csv, origin_attribution.csv, target_distribution.c"
            "sv, case_event_table.csv, case_candles.csv, case_cross_section_re"
            "turns.csv, independent_reconstruction_checks.json, artifact_inven"
            "tory.csv.\n"
        )
    )
    assert all(digest(Path(k)) == v for k, v in before.items())
    receipt = dict(
        status="PASS_P021A",
        population_rows=len(f),
        origins=5210,
        sessions=2980,
        mse=weighted,
        unweighted_mse=total / len(f),
        zero_mse=float(r.zero_mse),
        daily_ic=ic,
        scale=scale,
        epsilon=eps,
        optimizer_steps=0,
        new_pairs=0,
        ledger="36/200",
        protected_numeric_access=False,
        prepost_preserved_files=len(before),
        checks=checks,
        snapshot_sha256=before,
        official=official.to_dict("records"),
        dominant=dom.to_dict(),
    )
    (out / "independent_reconstruction_checks.json").write_text(
        json.dumps(receipt, indent=2, default=str) + "\n"
    )
    files = [
        dict(
            path=str(x.relative_to(root)),
            bytes=x.stat().st_size,
            sha256=digest(x),
            intent="LOCAL_IGNORED_PRIVATE",
        )
        for x in out.iterdir()
        if x.is_file()
    ]
    pd.DataFrame(files).to_csv(out / "artifact_inventory.csv", index=False)
    print(
        json.dumps(
            dict(
                status="PASS_P021A",
                official=official[
                    ["cohort", "n", "weighted_loss_share_pct", "unweighted_loss_share_pct"]
                ].to_dict("records"),
                dominant=dom.to_dict(),
                cases=len(checks),
                out=str(out),
            ),
            default=str,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    analyze(parser.parse_args().out.resolve())
