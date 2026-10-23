"""Independent P022 audit closure: quality cohorts, exact ranked membership and units."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.config import now, write_json
from lstm_data.hf1m_ft16_source import checked, ref
from lstm_data.magnitude_range_audit import session_weights
from lstm_data.objective_screen_loss import classes
from lstm_data.objective_screen_source import assert_frozen_design, ordered_targets, scoped_view
from lstm_data.visualization.hf1m_long import LongStudy


def verify(out: Path) -> None:
    assert_frozen_design(out)
    gate = json.loads((out / "stage_01_feature_audit_gate.json").read_text())
    for r in gate["files"] + [gate["report"]]:
        checked(r)
    dest = out / "stage1_verification"
    dest.mkdir(exist_ok=False)
    study = LongStudy.discover(Path.cwd())
    records = []
    quality_records = []
    recipe = json.loads((out / "stage1/inner_event_recipe.json").read_text())
    for split in ["inner_train", "inner_validation"]:
        v = scoped_view(study, split, stage=1)
        t = ordered_targets(v)
        w = session_weights(t)
        event = classes(t.TG20.to_numpy(), recipe["q95_abs_y"])
        quality = pd.read_parquet(
            study.file("P020_origin_quality_diagnostics.parquet"),
            filters=[("origin_id", "in", v.source.rows.origin_id.tolist())],
        )
        joined = t.merge(
            quality[
                [
                    "origin_id",
                    "assumed_zero_minute_count",
                    "price_proxy_minute_count",
                    "poor_volume_hour_count",
                    "inner_feature_fallback_cells",
                ]
            ],
            on="origin_id",
            validate="many_to_one",
            sort=False,
        )
        np.testing.assert_array_equal(joined.origin_id, t.origin_id)
        for k, name in enumerate(["NEG", "NORMAL", "POS"]):
            mask = event == k
            ww = w[mask] / w[mask].sum()
            for field in [
                "assumed_zero_minute_count",
                "price_proxy_minute_count",
                "poor_volume_hour_count",
                "inner_feature_fallback_cells",
            ]:
                a = joined.loc[mask, field].to_numpy()
                quality_records.append(
                    dict(
                        role=split,
                        event=name,
                        quality_field=field,
                        weighted_window_count=float(ww @ a),
                        weighted_positive_fraction=float(ww @ (a > 0)),
                        scope=(
                            "whole20-stock origin-window quality; not stock-specific "
                            "fault attribution"
                        ),
                    )
                )
        # Validate every saved unweighted mean and class mass against independent row counts.
        bins = pd.read_csv(out / "stage1/quintiles.csv")
        for _, g in bins.loc[bins.role.eq(split)].groupby(["feature", "representation"]):
            assert int(g.rows.sum()) == len(t)
            assert np.isclose(g.weight_mass.sum(), 1.0)
            valid = g.weight_mass.gt(0)
            np.testing.assert_allclose(g.loc[valid, ["NEG", "NORMAL", "POS"]].sum(axis=1), 1.0)
        if split == "inner_train":
            for pct in [1, 5]:
                count = len(t) * pct // 100
                for field in ["TG20", "numerator"]:
                    order = np.argsort(-abs(t[field].to_numpy()), kind="stable")
                    chosen = order[:count]
                    threshold = float(abs(t[field]).iloc[chosen[-1]])
                    tie_count = int(abs(t[field]).eq(threshold).sum())
                    records.append(
                        dict(
                            cohort=f"ranked_{field}_top{pct}",
                            count=count,
                            threshold=threshold,
                            boundary_ties=tie_count,
                            weighted_mass=float(w[chosen].sum()),
                            tie_rule="stable canonical origin then frozen stock order",
                        )
                    )
                    if field == "TG20":
                        zorder = np.argsort(
                            -abs(np.arcsinh(t.TG20.to_numpy() / recipe["scale"])), kind="stable"
                        )
                        np.testing.assert_array_equal(chosen, zorder[:count])
                origin = t.drop_duplicates("origin_id")
                k = len(origin) * pct // 100
                selected = origin.sort_values("cross_section_mad", kind="stable").iloc[:k]
                mask = t.origin_id.isin(selected.origin_id).to_numpy()
                assert mask.sum() == k * 20
                records.append(
                    dict(
                        cohort=f"ranked_origin_MAD_bottom{pct}",
                        count=int(mask.sum()),
                        threshold=float(selected.cross_section_mad.max()),
                        boundary_ties=int(
                            origin.cross_section_mad.eq(selected.cross_section_mad.max()).sum()
                        ),
                        weighted_mass=float(w[mask].sum()),
                        tie_rule="stable canonical origin order",
                    )
                )
            # Whole training population target reconstruction from frozen operands, no proxies.
            np.testing.assert_allclose(
                t.numerator / (t.cross_section_mad + v.source.fit["epsilon"]), t.TG20, rtol=1e-13
            )
            np.testing.assert_allclose(np.arcsinh(t.TG20 / recipe["scale"]), t.T2_z, rtol=1e-13)
    pd.DataFrame(records).to_csv(dest / "exact_ranked_membership.csv", index=False)
    pd.DataFrame(quality_records).to_csv(dest / "quality_by_signed_event.csv", index=False)
    # Bind/read the complete source-specific feature dictionary rather than guessing abbreviations.
    dictionary = study.report_file("P020_FEATURE_DICTIONARY_AND_AUDIT.md")
    (dest / "feature_dictionary_reference.md").write_text(dictionary.read_text())
    write_json(
        dest / "closure.json",
        dict(
            status="PASS_AUDIT_VERIFIED",
            at=now(),
            predecessor_gate=ref(out / "stage_01_feature_audit_gate.json"),
            feature_dictionary=ref(dictionary),
            checks=[
                "exact ranked counts",
                "monotone z-membership",
                "unique-origin MAD20expansion",
                "quintile mass and event disjointness",
                "source quality by signed event",
                "whole-train TG20/z operands",
                "no development numeric access",
            ],
            files=[ref(p) for p in dest.iterdir() if p.is_file()],
            new_starts=0,
            ledger=36,
        ),
    )
    print("PASS_AUDIT_VERIFIED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    verify(parser.parse_args().out)
