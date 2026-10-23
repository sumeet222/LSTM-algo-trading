"""Read-only P021C magnitude-range transformed-objective attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.magnitude_range_audit import range_masks, session_weights
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
    f["w"] = session_weights(f)
    # Derive weights from the verified population, not a fixed origins-per-day guess.
    f["z"] = np.arcsinh(f.TG20.to_numpy(dtype=np.float64) / scale)
    np.testing.assert_allclose(f.z, f.T2_z, rtol=1e-13, atol=1e-13)
    f["residual_z"] = f.z - f.raw_net_output.astype(np.float64)
    f["loss_z"] = f.residual_z**2
    f["weighted_loss_z"] = f.w * f.loss_z
    f["original_loss_CONTEXT"] = (f.TG20 - scale * np.sinh(f.raw_net_output)) ** 2
    y = f.TG20.to_numpy()
    maximum = float(np.abs(y).max())
    weighted = float(f.weighted_loss_z.sum())
    total = float(f.loss_z.sum())
    original_total = float((f.w * f.original_loss_CONTEXT).sum())
    np.testing.assert_allclose(
        f.groupby("session_date_et").w.sum(), 1 / f.session_date_et.nunique(), rtol=1e-14
    )
    np.testing.assert_allclose(f.w.sum(), 1, rtol=1e-14)
    np.testing.assert_allclose(
        weighted, f.groupby("session_date_et").loss_z.mean().mean(), rtol=1e-14
    )
    b = previous / "p021b_transformed_tail_2026-10-23_final"
    bclose = json.loads((b / "final_receipt.json").read_text())
    assert digest(b / "artifact_inventory.csv") == bclose["inventory_sha256"]
    inventory = pd.read_csv(b / "artifact_inventory.csv")

    def bound(name: str) -> Path:
        path = b / name
        ref = inventory.loc[inventory.path.eq(str(path.relative_to(root)))].iloc[0]
        assert digest(path) == ref.sha256 and path.stat().st_size == int(ref.bytes)
        return path

    obj = json.loads(bound("objective_reconciliation.json").read_text())
    np.testing.assert_allclose(weighted, obj["weighted_transformed_mse"], rtol=1e-14)
    ranked = pd.read_csv(bound("section1_raw_target_component_cohorts.csv"))
    bound("P021B_T2_S42_TRANSFORMED_TRAINING_TAIL_ATTRIBUTION.md").read_text()
    ref = pd.read_csv(previous / "metrics.csv")
    metric = ref.loc[ref.run_id.eq(RUN) & ref.partition.eq("refit")].iloc[0]
    np.testing.assert_allclose(original_total, metric.mse, rtol=3e-8)
    a99, m99 = range_masks(y, 0.99)
    a95, m95 = range_masks(y, 0.95)
    assert not (m99 & ~m95).any()

    def stats(name: str, mask: np.ndarray, cutoff: float) -> dict:
        g = f.loc[mask]
        n = len(g)
        mass = float(g.w.sum())
        wl = float(g.weighted_loss_z.sum())
        ul = float(g.loss_z.sum())
        return dict(
            cohort=name,
            cutoff=cutoff,
            rows=n,
            row_pct=100 * n / len(f),
            origins=g.origin_id.nunique(),
            sessions=g.session_date_et.nunique(),
            stocks=g.ticker.nunique(),
            weight_mass=mass,
            weight_mass_pct=100 * mass,
            weighted_loss_sum=wl,
            unweighted_loss_sum=ul,
            weighted_loss_pct=100 * wl / weighted,
            unweighted_loss_pct=100 * ul / total,
            conditional_weighted_mse=wl / mass if mass else None,
            conditional_unweighted_mse=ul / n if n else None,
            conditional_weighted_rmse=np.sqrt(wl / mass) if mass else None,
            conditional_unweighted_rmse=np.sqrt(ul / n) if n else None,
            original_weighted_loss_pct_CONTEXT=100
            * float((g.w * g.original_loss_CONTEXT).sum())
            / original_total,
        )

    records = [stats("ALL", np.ones(len(f), dtype=bool), 0)]
    signed = []
    disjoint = []
    groups = []
    moments = []
    for label, cutoff, mask in [("E99", a99, m99), ("E95", a95, m95)]:
        records.extend([stats(label, mask, cutoff), stats(label + "_complement", ~mask, cutoff)])
        positive = y >= cutoff
        negative = y <= -cutoff
        assert np.array_equal(positive | negative, mask) and not (positive & negative).any()
        for side, m in [("positive", positive), ("negative", negative)]:
            signed.append(dict(convention="GLOBAL_ABSOLUTE", side=side, **stats(label, m, cutoff)))
        for column in ["TG20", "z", "raw_net_output", "residual_z"]:
            for absolute in (False, True):
                vals = f.loc[mask, column].abs() if absolute else f.loc[mask, column]
                moments.append(
                    dict(
                        variable=column,
                        absolute=absolute,
                        mean=vals.mean(),
                        median=vals.median(),
                        minimum=vals.min(),
                        maximum=vals.max(),
                    )
                )
        for field in ["TG20", "raw_net_output"]:
            for sign in (-1, 0, 1):
                moments.append(
                    dict(
                        variable=field,
                        sign=sign,
                        count=int((np.sign(f.loc[mask, field]) == sign).sum()),
                    )
                )
        for by in ["ticker", "year", "session_date_et"]:
            ff = f.assign(year=f.session_date_et.str[:4])
            for key, g in ff.loc[mask].groupby(by):
                groups.append(
                    dict(
                        by=by,
                        key=key,
                        **stats(label, f.index.isin(g.index), cutoff),
                    )
                )
    for side, sign in [("positive", 1), ("negative", -1)]:
        side_max = float((sign * y)[sign * y > 0].max())
        for frac in (0.99, 0.95):
            cut = frac * side_max
            mask = sign * y >= cut
            signed.append(
                dict(
                    convention="SIDE_SPECIFIC_MAXIMUM",
                    side=side,
                    side_maximum=side_max,
                    **stats(str(frac), mask, cut),
                )
            )
    for name, m in [("E99", m99), ("E95_ONLY", m95 & ~m99), ("OUTSIDE_E95", ~m95)]:
        disjoint.append(stats(name, m, a99 if name == "E99" else a95))
    np.testing.assert_allclose(sum(x["weighted_loss_pct"] for x in disjoint), 100, atol=1e-12)
    np.testing.assert_allclose(sum(x["unweighted_loss_pct"] for x in disjoint), 100, atol=1e-12)
    assert sum(x["rows"] for x in disjoint) == len(f)
    # Independent scalar source reconstruction for all primary rows and both signs.
    q = s.table("candles_quality").set_index(["step", "ticker"])
    origins = s.table("origins").set_index("origin_id")
    samples = set(f.index[m95])
    samples.update(f.nlargest(4, "TG20").index)
    samples.update(f.nsmallest(4, "TG20").index)
    checks = []
    for i in sorted(samples):
        row = f.loc[i]
        o = origins.loc[row.origin_id]
        returns = []
        for symbol in SYMBOLS:
            entry = q.loc[[(int(o.entry_index), symbol)], :].iloc[0]
            exit_ = q.loc[[(int(o.exit_index), symbol)], :].iloc[0]
            assert entry.genuine_close and exit_.genuine_close
            returns.append(float(np.log(float(exit_.close) / float(entry.close))))
        median = float(np.median(returns))
        mad = float(np.median(np.abs(np.array(returns) - median)))
        r = returns[SYMBOLS.index(row.ticker)]
        yy = (r - median) / (mad + eps)
        zz = float(np.arcsinh(yy / scale))
        np.testing.assert_allclose(
            [r, median, mad, yy, zz],
            [row.return_4h, row.cross_section_median, row.cross_section_mad, row.TG20, row.z],
            rtol=1e-11,
            atol=1e-12,
        )
        np.testing.assert_allclose(
            (zz - float(row.raw_net_output)) ** 2, row.loss_z, rtol=1e-11, atol=1e-12
        )
        checks.append(
            dict(
                ticker=row.ticker,
                origin_id=row.origin_id,
                status="PASS",
                TG20_reconstructed=yy,
                z_reconstructed=zz,
            )
        )
    comparisons = []
    for pct, cutoff, mask in [(1, a99, m99), (5, a95, m95)]:
        r = ranked.loc[
            ranked.cohort.eq(f"RAW_TG_ABS_TOP_{pct}PCT")
            & ranked.definition.eq("stable_rank_topK")
            & ranked.side.eq("cohort")
        ].iloc[0]
        rankmask = f.index.isin(
            f.assign(mag=f.TG20.abs(), stock=f.ticker.map({v: i for i, v in enumerate(SYMBOLS)}))
            .sort_values(["mag", "origin_id", "stock"], ascending=[False, True, True])
            .head(len(f) * pct // 100)
            .index
        )
        np.testing.assert_allclose(
            stats("ranked", rankmask, 0)["weighted_loss_pct"], r.weighted_loss_share_pct, rtol=1e-14
        )
        comparisons.extend(
            [
                dict(
                    convention="MAGNITUDE_RANGE",
                    level=pct,
                    rows=int(mask.sum()),
                    row_pct=100 * mask.sum() / len(f),
                    weighted_transformed_loss_pct=stats("range", mask, cutoff)["weighted_loss_pct"],
                ),
                dict(
                    convention="P021B_RANKED_PERCENTILE",
                    level=pct,
                    rows=int(r.rows),
                    row_pct=100 * r.rows / len(f),
                    weighted_transformed_loss_pct=r.weighted_loss_share_pct,
                ),
            ]
        )
    out.mkdir(parents=True)
    (out / ".gitignore").write_text("*\n!.gitignore\n")
    for name, rows in [
        ("magnitude_range_cohorts", records),
        ("signed_extremes", signed),
        ("disjoint_loss_reconciliation", disjoint),
        ("stock_year_date_concentrations", groups),
        ("cohort_moments_and_signs", moments),
        ("comparison_to_p021b", comparisons),
    ]:
        pd.DataFrame(rows).to_csv(out / (name + ".csv"), index=False)
    extreme = f.loc[m95].copy()
    extreme["E99"] = m99[m95]
    extreme["E95"] = True
    # Source prediction columns in original units remain explicitly context-only.
    extreme = extreme.rename(
        columns={
            k: "original_" + k + "_CONTEXT"
            for k in ["error", "squared_error", "abs_error", "zero_squared_error"]
        }
    )
    extreme.to_csv(out / "magnitude_range_extreme_rows.csv", index=False)
    primary = pd.DataFrame(records).loc[
        lambda g: g.cohort.isin(["E99", "E95"]),
        [
            "cohort",
            "cutoff",
            "rows",
            "row_pct",
            "weighted_loss_pct",
            "unweighted_loss_pct",
            "weight_mass_pct",
        ],
    ]
    report = (
        f"""# P021C T2 seed42 magnitude-range tail loss

## 1. Executive answer

Maximum absolute original target M={maximum!r}.
E99 and E95 are inclusive magnitude-range cutoffs anchored at zero, not ranked quantiles.
Weighted final-checkpoint transformed MSE={weighted!r}; unweighted={total / len(f)!r}.
"""
        + md(primary)
        + """
These very rare near-maximum readings account for only the loss shares shown above.
The broader ranked tails are a different population and can still matter materially.
This is in-sample final-checkpoint loss, not causal credit for historical optimization.

## 2. Definitions and cohort construction

r=log(genuine_exit/genuine_entry); m=median20(r); n=r-m;
D=median20(|r-m|); y=n/(D+epsilon); z=asinh(y/s); L=(z-saved_raw_zhat)^2.
E99={|y|>=.99M}; E95={|y|>=.95M}; M=max|y| over all104200refit rows.
IEEE float64 multiplication/comparison includes equality; no rounding before membership.
Weights=1/(number_sessions × admitted_origins_that_session ×20), derived from data.
Contribution means share of squared-loss sum; RMSE is not additive.
"""
        + f"""\nmin(y)={float(y.min())!r}; max(y)={float(y.max())!r}; M={maximum!r};
.99M={a99!r}; .95M={a95!r}; s={scale!r}; epsilon={eps!r}.\n"""
    )
    report += "\n## 3. Primary global-magnitude results\n\n" + md(primary)
    report += (
        "\nConditional transformed MSE/RMSE, complementary and full-population comparison:\n\n"
        + md(
            pd.DataFrame(records)[
                [
                    "cohort",
                    "rows",
                    "conditional_weighted_mse",
                    "conditional_weighted_rmse",
                    "conditional_unweighted_mse",
                    "conditional_unweighted_rmse",
                ]
            ]
        )
    )
    report += """\n## 4. Positive versus negative extremes\n\nGlobal cutoff sides partition each
primary cohort; side-specific maxima use a separate convention. Zero counts are genuine
empty sets, with conditional metrics undefined.\n\n""" + md(
        pd.DataFrame(signed)[
            [
                "convention",
                "side",
                "cohort",
                "cutoff",
                "rows",
                "row_pct",
                "weighted_loss_pct",
                "unweighted_loss_pct",
            ]
        ]
    )
    report += """\n## 5. Disjoint loss accounting\n\nE99 and E95 overlap; only these three
disjoint sets may be added:\n\n""" + md(
        pd.DataFrame(disjoint)[
            ["cohort", "rows", "weighted_loss_pct", "unweighted_loss_pct", "weight_mass_pct"]
        ]
    )
    report += (
        "\n## 6. Per-stock and per-year concentrations, exact observations and source quality\n\n"
        + md(
            pd.DataFrame(groups)[
                ["cohort", "by", "key", "rows", "weighted_loss_pct", "unweighted_loss_pct"]
            ]
        )
    )
    report += """\nExact selected readings (full operand/proxy/volume/fallback details in
[CSV](magnitude_range_extreme_rows.csv)):\n\n""" + md(
        extreme[
            [
                "ticker",
                "origin_id",
                "TG20",
                "z",
                "raw_net_output",
                "residual_z",
                "loss_z",
                "w",
                "weighted_loss_z",
                "E99",
            ]
        ]
    )
    report += """\nSigned/absolute target, z, prediction and residual moments and sign
counts: [cohort_moments_and_signs.csv](cohort_moments_and_signs.csv). Source quality and
original-scale error shares are secondary context, saved separately in the cohort/event
CSVs.\n"""
    report += (
        "\n## 7. Contrast to P021B ranked-percentile analysis\n\n"
        + md(pd.DataFrame(comparisons))
        + """
Magnitude-range cutoffs can select far fewer rows than ranked1%/5%: targets are not
uniform across their numerical range. A small near-maximum contribution qualifies
claims about the single most extreme readings; it does not negate concentration in
the wider ranked tail. Event sets and shares are not identical.

## 8. Numerical verification, provenance and limitations

Only pinned mito0o852/OHLCV-1m revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56,
P019B→P020FT16/TG20/MODEL_INPUT→P021 recovery_v1, final7-epoch T2/seed42 refit.
104200unique stock/origin pairs,5210complete20-name origins,2980sessions. Native
saved network predictions are z, not once-inverted y predictions. No inference or
optimizer was run. Final-checkpoint evaluation differs from online dropout-active
loss at changing weights. Source-derived numeric reports remain private/local/ignored.
Private-use rights, source/action/dividend/publication timing and volume-basis
assumptions remain qualified; genuine endpoints are reference closes, not trade fills.
Independent full20-return reconstruction includes both signs and every primary row;
weights and totals reconcile with P021B. Signed primary partitions, E99 nesting,
three-way loss conservation and separate ranked-tail cross-checks pass. No legacy
numerical inputs,2026numeric access, dataset changes, dashboard changes or new fits.
Ledger remains36/200. Detailed verification/hashes: analysis_verification.json.
"""
    )
    (out / "P021C_T2_S42_MAGNITUDE_RANGE_TAIL_LOSS_REPORT.md").write_text(report)
    assert all(digest(Path(k)) == v for k, v in before.items())
    verification = dict(
        status="PASS_P021C",
        gates={
            k: "PASS"
            for k in [
                "A_identity",
                "B_reconstruction",
                "C_memberships",
                "D_loss_accounting",
                "E_report",
            ]
        },
        run_id=RUN,
        input_contract=s.plan["input_contract"],
        checkpoint=checkpoint,
        prediction=result["artifacts"]["refit_predictions.parquet"],
        source_revision=s.plan["source_revision"],
        symbols=list(SYMBOLS),
        rows=len(f),
        origins=5210,
        sessions=2980,
        scale=scale,
        epsilon=eps,
        M=maximum,
        minimum_y=float(y.min()),
        maximum_y=float(y.max()),
        weighted_z_mse=weighted,
        unweighted_z_mse=total / len(f),
        primary=primary.to_dict("records"),
        sample_checks=checks,
        preserved_sha256=before,
        optimizer_steps=0,
        new_pairs=0,
        ledger="36/200",
        protected_numeric_access=False,
    )
    (out / "analysis_verification.json").write_text(
        json.dumps(verification, indent=2, default=str) + "\n"
    )
    print(
        json.dumps(
            dict(status="PASS_P021C", M=maximum, primary=primary.to_dict("records"), out=str(out)),
            default=str,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    analyze(parser.parse_args().out.resolve())
