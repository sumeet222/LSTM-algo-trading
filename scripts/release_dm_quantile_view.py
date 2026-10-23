"""Seal completed P023 view bindings and document real controls; never starts training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from lstm_data.config import write_json
from lstm_data.hf1m_ft16_source import ref


def release(plan_path: Path) -> None:
    p = plan_path.parent
    assert json.loads((p / "stage_5_gate.json").read_text())["status"] == "PASS_COLLECTIVE"
    files = {}
    collective = p / "collective_v1"
    guide = Path("docs/track_a/P023_EXPLORER_GUIDE.md")
    examples = []
    for arm in ["DM1", "QR1", "SS1"]:
        root = p / (arm + "_diagnostics_v1")
        supp = root / "supplement_v1"
        assert json.loads((supp / "verification.json").read_text())["status"] == "PASS_SUPPLEMENT"
        for role in ["inner_train", "inner_validation", "refit", "development"]:
            for name in ["population.parquet", "metrics.json"]:
                files[f"{arm}/{role}/{name}"] = ref(root / role / name)
        files[arm + "/conditional_scores.json"] = ref(supp / "conditional_scores.json")
        files[arm + "/objective_components_by_cohort.csv"] = ref(
            supp / "objective_components_by_cohort.csv"
        )
        if arm == "DM1":
            for role in ["inner_train", "inner_validation", "refit", "development"]:
                files[arm + "/" + role + "/sign_calibration.json"] = ref(
                    supp / (role + "_sign_calibration.json")
                )
        witness = supp / "witnesses"
        for name in [
            "cases.parquet",
            "case_candles.parquet",
            "case_features.parquet",
            "case_20_returns.parquet",
        ]:
            files[arm + "/" + name] = ref(witness / name)
        cases = pd.read_parquet(witness / "cases.parquet")
        selected = cases.loc[
            cases.ticker.eq({"DM1": "AAPL", "QR1": "AMZN", "SS1": "TSLA"}[arm])
        ].iloc[0]
        examples.append(
            f"- **{arm} → Exact Cases → P023 exact case {selected.case_id}**: "
            f"{selected.ticker}, origin `{selected.origin_id}`."
        )
    files["SS1/sampler_exposure.csv"] = ref(
        p / "SS1_diagnostics_v1/supplement_v1/sampler_exposure.csv"
    )
    guide.write_text(
        """# P023 explorer guide — 5–10 minutes

Launch `./scripts/run_track_a_dashboard.sh`, then **Explore → HF1M Long — Direction / 
Quantiles / Sampling (P023)**. This is a section in the existing app.

1. **P023 view → Comparisons**, **P023 role → development**. Change **P023 model** among 
DM1/QR1/SS1. Inspect task-specific prefix constants and saved T2/42,T2/123,ZERO. QR1 
median MSE is descriptive, not a fair mean-optimum comparison; proper pinball/coverage is 
primary.
2. **Optimization / Gradients** separates calibration/refit actual objective curves and 
gradient percentiles/clipping. DM1 uses signCE+magnitudeMSE; QR1 uses pinball; SS1 uses 
sampled importance-corrected zMSE. Do not compare loss magnitudes across tasks.
3. **Head Outputs** and **P023 output stock** show DM1 
probability/magnitudes/cancellation, QR1 ordered .05/.50/.95 bands and calibration, or SS1
 forecasts plus actual sampler exposure. Probabilities and quantiles are different 
objects. Predicted magnitude alone is not success.
4. **Actual-Objective Tails** → **P023 cohorts** compares rank top1/top5, train-maximum 
ranges and numerator/MAD disjoint groups. Count/weight/loss percentages differ. 
Overlapping groups do not add; RMSE is not additive. Attribution is final-checkpoint 
dropoutOFF, distinct from online dropoutON.
5. **Exact Cases** uses saved in-sample refit witnesses independent of role selector. 
Inspect raw heads, true target components, source quality,52scheduled candles 
and48×16native/scaled features. First48hours are inputs and final4are outcomes. Verified 
example selections:

"""
        + "\n".join(examples)
        + """

6. **History / Features** → **P023 history stock/start/end** gives all20stock genuine 
OHLCV plus closing stubs, July2010–December2025,≤93days per request. **P023 feature 
recipe/M2 context/channel** selects all16native/scaled features. Missing/proxy/volume 
flags remain visible. Dates are checked before numeric loading.
7. **Guide** shows these controls. Existing P021/P022 and legacy study sections remain in 
Explore. Protected2026query/widget/role requests are denied; no fallback source.

Roles: inner_train calibration in-sample; inner_validation selected epochs; refit fresh 
in-sample; development183origins/3660rows/109sessions exploratory. Ledger44/200. No 
seed123newarm, combination, trading or confirmation access. All numeric artifacts remain 
private/local.
"""
    )
    files["guide.md"] = ref(guide)
    for name in ["scores.json", "optimization.csv", "paired_differences.csv", "cohorts.parquet"]:
        files[name] = ref(collective / name)
    write_json(
        p / "viewer_manifest.json",
        dict(status="PASS_COLLECTIVE", ledger=44, files=files, plan=ref(plan_path)),
    )
    write_json(
        Path("configs/track_a_p023_visualization_v1.json"),
        dict(
            schema_version=1,
            manifest=ref(p / "viewer_manifest.json"),
            ledger=44,
            protected_numeric_access=False,
        ),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--plan", type=Path, required=True)
    release(p.parse_args().plan)
