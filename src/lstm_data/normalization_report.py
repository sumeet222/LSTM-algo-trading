"""Compact audit reader and reproducible evidence-led human documents, never training."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import digest
from .visualization.definitions import FEATURES
from .visualization.loaders import Catalog, ViewUnavailable, read_json, verified


@dataclass(frozen=True)
class AuditPacket:
    catalog: Catalog
    manifest: dict

    @classmethod
    def discover(cls, catalog: Catalog) -> AuditPacket:
        ref = catalog.config.get("normalization_audit")
        if ref is None:
            raise ViewUnavailable("Package012A audit not registered; no computations started.")
        manifest = read_json(catalog.root, ref)
        if manifest.get("package") != "TA012A_FT0_READONLY_v1":
            raise ViewUnavailable("Unsupported normalization audit.")
        if manifest.get("source") != catalog.config["manifest"]:
            raise ViewUnavailable("Audit/source binding mismatch; no fallback.")
        if (
            manifest.get("recipes") != catalog.config["recipes"]
            or manifest.get("confirmation_numeric_rows") != 0
        ):
            raise ViewUnavailable("Audit/recipe or confirmation binding mismatch.")
        return cls(catalog, manifest)

    def table(self, name: str) -> pd.DataFrame:
        if name not in self.manifest["artifacts"] or not name.endswith(".csv"):
            raise ViewUnavailable("Not a registered compact audit table.")
        return pd.read_csv(
            verified(self.catalog.root, self.manifest["artifacts"][name]),
            float_precision="round_trip",
        )

    def json(self, name: str) -> dict:
        if name not in self.manifest["artifacts"]:
            raise ViewUnavailable("Not a registered audit document.")
        return read_json(self.catalog.root, self.manifest["artifacts"][name])


def publish_manifest(catalog: Catalog, out: Path) -> dict:
    """Seal only small read-only display artifacts; protected scientific bindings stay fixed."""
    names = (
        "ft0_normalization_distribution.csv",
        "ft0_temporal_drift.csv",
        "ft0_stock_scale_comparison.csv",
        "ft0_tail_and_fallback_audit.csv",
        "feature_replay_examples.csv",
        "histograms.json",
        "population_and_recipe_bindings.json",
        "tail_identity_sets.json.gz",
    )
    artifacts = {
        name: dict(path=str((out / name).relative_to(catalog.root)), sha256=digest(out / name))
        for name in names
    }
    resolved = out / "feature_replay_examples_resolved.csv"
    if resolved.exists():
        artifacts["feature_replay_examples.csv"] = dict(
            path=str(resolved.relative_to(catalog.root)), sha256=digest(resolved)
        )
    tails = out / "tail_identity_sets_verified.json.gz"
    if tails.exists():
        artifacts["tail_identity_sets.json.gz"] = dict(
            path=str(tails.relative_to(catalog.root)), sha256=digest(tails)
        )
    return dict(
        package="TA012A_FT0_READONLY_v1",
        source=catalog.config["manifest"],
        recipes=catalog.config["recipes"],
        confirmation_numeric_rows=0,
        artifacts=artifacts,
    )


def write_documents(out: Path) -> None:
    d = pd.read_csv(out / "ft0_normalization_distribution.csv")
    p = d.loc[d.symbol.eq("POOLED") & d.representation.eq("scaled")]
    b1 = p.loc[p.feature.eq("B1") & p.partition.eq("Development")]
    v2 = p.loc[p.feature.eq("V2") & p.partition.eq("Development")]
    oracles = pd.read_csv(out / "independent_feature_oracles.csv")
    registry = """# FT0 registry and equations — source-defined audit

Native means a registered engineered channel, not raw OHLCV. Every channel here
is dimensionless: log ratios, return ratios or bounded indicators. Scaled means
the saved pooled transform followed by the exact neural float32 conversion.
No extra Gaussianization, per-stock fitting or clipping is applied.

| Channel | Actual native formula | Support / source equation |
|---|---|---|
"""
    for feature, label in FEATURES.items():
        support = (
            "[-1,1]"
            if feature in ("B2", "T2", "T5")
            else ">=0"
            if feature == "B1"
            else "signed real"
        )
        registry += f"| {feature} | {label} | {support} |\n"
    registry += """
Equations: `stock_features.py:149` apply_component_floors; `:205` scheduled
hour/daily histories; `:56` EMA/Wilder updates; `:86` bounded RSI; `:316` native
bar/technical features. `pretraining_transforms.py:118` replaces M2 using its
own origin-matched mature-return RMS/floor, not hourly RMS. The other scalar
formulae use the exact saved floors. Q1/Q2 are **signed log volume ratios**,
not positive raw volumes, and already use approved additive stock-specific
pseudocounts (`TA_P2_FT0_Q_VOLUME_001_v1.json`). No second generic log is justified.

Clocks/warm-up: current completed hourly OC return is included in RMS12/60;
12/12 and57/60 valid, at most2 consecutive misses. Daily features use prior
completed full sessions, including genuine closing stub volume; RMS63 requires
60/63. Q1 uses19/20 matching slots; Q2 uses5/5 and57/60. M2 uses19/20 and57/60
previous ordinary origin-specific outcomes, mature by the historical step,
never today's target. EMA6/18/24/72 seed at first good full-hour close then
require360 updates; recent72 need69 good/no>2 misses. Wilder14 requires14
initial consecutive changes plus140 updates and the same recent coverage;
missing bars freeze state and do not bridge a synthetic recovery delta.
Native missing/quality reasons remain available; no imputation. Unknown observed
publication/action vintage is not converted into a certified live clock.

Scaling: exactly M1 M2 M3 M4 V1 V2 V3 B1 Q1 Q2 T1 T3 T4 use pooled training-prefix
median/unscaled MAD. B2 T2 T5 use identity, with only float32 rounding.
`pretraining_transforms.py:195` fits unique symbol/session/slot keys; M2 instead
uses symbol/session/origin and50/50 origin weights. Daily-locked channels other
than M2 still use the registered hourly keys. These are not48 duplicated window
observations. Every recorded center/scale/method and stock-specific floor or
pseudocount is in ft0_tail_and_fallback_audit.csv and floor_recipe_parameters.csv;
scope, source/action/population IDs and actual fitting/constructing clocks are
in population_and_recipe_bindings.json.

Fallback code: `ft0_transforms.py:357`: positive MAD, then IQR/1.349, then weighted
population SD; exact zero SD selects center/scale1 and CONSTANT->zero. Later
variation in a CONSTANT channel is a separate diagnostic, not clipping.
**Document/code discrepancy:** a synthetic nonzero constant [7,7,7] yields
SD8.881784197001252e-16 due to weighted-mean rounding, selecting SD instead of
the D4 constant-to-zero contract. No active recipe uses this branch: all52
recorded scaled-channel fits use positive MAD. Historical math is untouched.
Separate guarded repair review is required before relying on that fallback.

Primary distributions deduplicate hourly observations. M2 necessarily retains
origin in its key because its two values can differ at one timestamp; its fit
population additionally collapses repeated within-session values. For example,
WF1 inner training has6,920 M2 feature fit keys, versus6,880 stock/forecast labels;
four early-close sessions represented in lawful input histories explain the
difference. All four exact fit-population hashes reproduce. OOS masks are the
original saved masks; first16 potential validation/development origins are
excluded where their48-step history precedes the recipe stop, not intersected
away to improve a comparison. Training warm-up is excluded from fit statistics.

Definition notes: constant_rate=max multiplicity/finiteN; near-zero=|x|<=1e-8;
SD uses ddof0; Bowley skew=(p75+p25-2median)/IQR. p-prefixed columns are signed;
abs_p columns summarize |value|. Rates use finite canonical observations.
Temporal rows are non-overlapping pooled months and stock/pooled quarters;
segments separate origin/slot, DST offsets and early-close input sessions.
Hypothetical clipping preserves order but may create ties; cross-stock pair
loss uses only complete five-stock sections, reporting incomplete counts.
All tail identities (not only examples) are in tail_identity_sets.json.gz;
model window exposure counts are separate from primary unique-key statistics.
These observations are dependent; no IID test, change-point significance or
predictive-importance claim follows from these summaries.
"""
    (out / "feature_registry_and_equations.md").write_text(registry)
    oracle_doc = f"""# Feature dependencies and independent oracles

{len(oracles):,} source/model-input checks, {int(oracles.passed.sum()):,} passed.
All16 channels and all5 stocks are represented. Fixed examples span AAPL's
2020-08-28/31 split basis,2020-12-09, both sides of2021-03 DST,2023-11-24 early
close and2024-06-28 archive edge. Additional family maxima are selected only
by |scaled feature|; no target correlation or importance scoring is used.

normalization_oracles.source_replay reads genuine immutable source windows of
at most91 dates per call, temporarily in RAM, through the last permitted example.
It independently combines the two source half-hours, derives full-session
daily closes/volumes including stubs, and separately streams EMA/Wilder state
from its actual first seed. No partial-history EMA seed approximation.
native_oracle independently checks hourly/daily RMS, momentum, older momentum,
bar shape, prior matching-slot/full-session volume ratios/pseudocounts, SMA,
signs, normalized EMAs and bounded RSI. M2 recomputes only matured historical
origin-matched price returns with nominal+3minute maturity, not new TG0 labels.

For each check, a **real original registered consuming forecast's48-step index**
is located. Its saved recipe is applied through CandidateView.row and the exact
real_bridge_data.build_view float32 conversion; the independent scalar transform
must match bitwise. Native equations tolerate relative/absolute1e-10, reflecting
independent floating summation/recursive state arithmetic. No windows are saved.
**Limit:** historical neural batches/tensors were not persisted. This verifies
the identical frozen constructor and registered masks/recipes, not a nonexistent
captured batch. Any material defect would HOLD its affected channel branch;
none occurred in these actual-input checks.

independent_feature_oracles.csv includes equations' values, identity and consuming
cutoff. feature_replay_examples.csv contains compact per-stock/channel/population
maxima with source lineage and recipe, not all feature arrays. Mathematical
synthetic cases cover floors, pseudocounts, all fallback branches and the disclosed
nonzero-constant rounding gap; synthetic observations never enter audit tables.

Large B1 values are genuine wide source high-low ranges divided by ordinary
positive recorded scales; no fitted degeneracy was found. T3's SBUX May2024
negative extreme replays from causal EMA state, including the genuine overnight
change, on the same retrospective split basis. Corporate action vintage,
economic explanation (earnings/news) and true historical publication remain
unverified: lawful price mechanics do not independently certify those facts.
"""
    (out / "feature_dependency_and_oracles.md").write_text(oracle_doc)
    findings = "# Normalization hypotheses ranked — proposals only\n\n"
    findings += "All52 scaled-channel fits use MAD; all12 bounded recipes use identity. "
    findings += (
        "No current scale is degenerate; no bounded violation or input mismatch was found. "
        "A three-MAD event is not a three-standard-deviation event. "
        "Heavy tails alone do not establish bad normalization.\n\n"
    )
    for _, r in b1.iterrows():
        findings += (
            f"- {r.fold} B1 development: max {r['max']:.6g}, |scaled|p99 {r.abs_p99:.6g}, "
            f">10 rate {100 * r.abs_gt_10_rate:.3f}%, N={r.observed}.\n"
        )
    for _, r in v2.iterrows():
        findings += (
            f"- {r.fold} V2 development: median {r['median']:.6g}, IQR {r.IQR:.6g} "
            "in original pooled training-MAD units.\n"
        )
    findings += """
These are measured dynamic-range and regime-shift mechanisms, not instability
proofs. Per-stock IQR dispersion differs moderately (e.g. T1/T4), while B1
stock IQR/pool ratios are about0.89–1.17. No single stock owns all range tails.
Feature dependence is reported separately: normalization cannot remove the
algebra V3=V1−V2, EMA horizon dependence or establish causation.

## Restrained future 012B matrix

1. **N-B1 monotone tail compression (first candidate).** Hypothesis: rare genuine
   wide ranges dominate B1 input amplitude; compressing only this channel reduces
   leverage while retaining order. For native x=log(H/L)>=0, propose
   q=asinh(x/s_train), s_train=median strictly-positive native B1 on the same
   pooled training keys, followed by a freshly registered train-only robust
   center/scale of q. Inner and refit each have their own recipe. This deliberately
   adds a second transform to a log range; it is justified only by measured tails,
   not a generic log of already logged features. Desirable effect: lower rare
   amplitudes without hard ties. Harm: compression may remove useful volatility
   contrast and changes derivatives. Compare original C0 vs B1-only treatment;
   leave all other15 channels, TG0 and training protocol fixed.
2. **N-V12 causal rolling normalization (second, weaker candidate).** Hypothesis:
   measured V1/V2 level drift makes a long pooled prefix center less representative.
   Propose z=(x−median_past60sessions)/(max(MAD_past60sessions,0.25*a_train)) only
   for V1/V2, pooling the same5 names on unique prior full-hour keys strictly
   before t. The60-session horizon and0.25floor are proposed predeclaration
   choices, not tuned or approved here. Need complete prior coverage, explicit
   warm-up/failure rules, original native floors, exact per-step cutoffs and
   no fit on later observations. Desired: stable local level/dispersion. Harm:
   erases persistent volatility state/cross-stock contrasts and may amplify
   quiet regimes; V3 is deliberately unchanged as a one-block test. Compare
   C0 vs V1/V2-only normalization, no target transforms combined.

No active variants, alternative scalers or transformed input stores are created.
Human 012B approval must freeze hypothesis, causal population/recipe identities,
primary metric (suggest existing equal-day Rank IC with canonical MSE guard),
failure/go-no-go criteria, seeds, matched budget and multiplicity plan before
training. No pair reservation now. Preserve original C0 plus two independent
one-factor variants; do not combine them in the first comparison.

Per-stock scaling is lower priority: heterogeneity exists, but its magnitude
does not alone outweigh losing common peer-comparable units. Q1/Q2 are already
signed logs with lawful pseudocounts; V1/V2 are already logged RMS, so another
generic log is unsuitable. Retain B2/T2/T5 identity absent measured pathology.
No stronger MAD floor is supported by the52 current fits. The synthetic constant
fallback discrepancy needs separate engineering review, not retroactive input
or model edits. Five-stock cross-sectional normalization risks unstable MADs,
same-timestamp availability and selection/cohort effects; do not add it now.

WF1/WF2 have been examined repeatedly. Any selected variant and later score
comparison on them is exploratory, not untouched confirmation or selection-adjusted
evidence. No input variant was ranked by target correlation, model scores or P&L.

## Separate target-normalization handoff

TG0 remains (future4h return−five-stock median)/(cross-sectional MAD+training
epsilon). It is separate from FT0 historical RMS/pooled feature MAD. Package010C
already preserves the small-cross-sectional-MAD examples and exact TG0 ranges;
reuse its bound examples rather than constructing new labels. A future target
study needs its own hypothesis/population/maturity/units and inverse-evaluation
rules. No target variant, T2 combination or automatic 012B activation here.
"""
    (out / "normalization_hypotheses_ranked.md").write_text(findings)
    (out / "visualization_walkthrough.md").write_text("""# Five-minute normalization walkthrough

Run `./scripts/run_track_a_dashboard.sh`; --check/--smoke validate setup/localhost.
Start Here → Package012A normalization audit opens the existing explorer.
The compact audit expander has independent fold, feature, partition and stock/pooled
controls. Select B1 / WF2 / Development. Native and scaled histograms use all
canonical observations (bin counts, not an extreme sample). Compare its per-stock
table and monthly/quarterly drift. Recipe parameters and source/coverage are shown.
Select V2 to inspect its development median shift, not interpret it as predictive
importance or demand a Gaussian histogram. Select B2/T2/T5 for bounded identity.

Choose a registered normalization example, then Open normalization example.
For CMCSA /2024-01-25 B1 slot1 use WF2. The existing Price & Features chart shows
genuine30minute candles and aligned adjusted-share volume, with exact UTC/ET hover.
Expand the actual48-step Feature Scaling Explorer; its consuming forecast identity
is preserved. To browse without fold navigation, choose Partition → Full data,
then CMCSA / Jump to date2024-01-25, B1, explicit WF2/refit, Both. Native and
scaled panels have separate axes. For earlier direct checks use AAPL2020-12-09
with WF1/refit and M1. Full data is chart-only, not a fitting population.

The original live Feature Scaling Explorer supplies bounded matched time traces
and native/scaled histograms; the new expander supplies full-population grouped
comparisons. It does not create another app or recompute supervised outputs.
Out-of-recipe dates are unavailable. Confirmation2024-07–2025-06 stays numerically
locked, including prices; date selection does not grant access. Source/action/
publication/universe/rights limitations remain ASSUMPTION_CONDITIONAL. Targets
and future horizon markers in the existing TG inspector are EX-POST, not features.
""")
    status = json.loads((out / "checks.json").read_text())["status"]
    (out / "human_review_card.md").write_text(f"""# Package012A human review card

**{status} — descriptive audit completed; no 012B authority.**

| Item | Status |
|---|---|
| Four exact fit-population hashes and original evaluation masks | PASS |
| 13 robust +3 identity channels across both folds/prefixes | PASS —52MAD/12identity |
| Native/source equations and actual float32 constructor checks | PASS —{len(oracles):,} rows |
| Clipping diagnostics, tails, drift/stock/slot dependence | PASS — original values retained |
| Protected confirmation, no new fits/pairs | PASS —0 numeric confirmation rows;24/40 preserved |
| Nonzero constant fallback | HOLD for future repair; synthetic only, no active recipe affected |
| Publication/action/rights/PIT/course/shared gates | Existing independent HOLDs remain |
| Software/static/UI verification | See validation.json and focused logs, appended before handoff |
| Human editor Problems refresh / native browser appearance | Pending human confirmation |

Decisions: whether to authorize either separately specified 012B feature variant;
whether to authorize a narrow nonzero-constant fallback repair with retrospective
audit. No training, target combination or confirmation numeric viewing is authorized
by this report. No claim that less heavy-tailed or Gaussian-looking inputs improve alpha.
""")
