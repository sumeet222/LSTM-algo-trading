"""Decision documents; all cohort counts come from the measured source census."""

from __future__ import annotations

from pathlib import Path

from .config import digest, write_json


def documents(out: Path, manifest: dict, decision: dict, quality: dict, config_path: Path) -> None:
    revision = manifest["revision"]
    base = "https://huggingface.co/datasets/twelvedata/financial-world-model"
    source = f"{base}/tree/{revision}/bars_1h"
    card = f"{base}/blob/{revision}/README.md"
    proposal = decision.get("proposal")
    shortlist = "No20-stock cohort meets the declared timestamp/quality criteria.\n"
    chronology = "Revised dates,20names, genuine hours: UNVERIFIED if no cohort qualifies.\n"
    if proposal:
        shortlist = (
            "**Technical primary20, subject to independent rights/adjustment holds:** "
            + ", ".join(proposal["primary"])
            + ".\n\nBackups: "
            + ", ".join(proposal["backups"])
            + ".\n"
        )
        chronology = (
            f"Common interval {proposal['start']} through {proposal['end']}: "
            f"{proposal['usable_stock_hours']:,} usable of "
            f"{proposal['expected_stock_hours']:,} expected stock-hours; "
            f"{proposal['missing_stock_hours']:,} missing/invalid "
            f"({1 - proposal['coverage']:.6%}).\n\n"
        )
        chronology += "|Partition|Start|End|Calendar sessions|48h+4h common origins|\n"
        chronology += "|---|---|---|---:|---:|\n"
        for r in proposal["splits"]:
            count = r["complete_48historical_and4future_hours_origins"]
            chronology += (
                f"|{r['partition']}|{r['start']}|{r['end']}|{r['calendar_sessions']}|{count}|\n"
            )
        chronology += (
            f"\nWarmup reserved {proposal['warmup']['start']}–"
            f"{proposal['warmup']['end']} "
            f"({proposal['warmup']['calendar_sessions']}exchange sessions, "
            f"{proposal['warmup'].get('complete_regular_sessions')}complete regular sessions). "
            "These are conditional row-presence/quality counts, not actual FT0/TG0 "
            "eligibility. Original daily/EMA warmups and corporate actions require "
            "a separately approved hourly-native methodology. Raw held-out source "
            "quality was inspected; model outcomes/targets were never calculated. "
            "Freeze held-out dates before modeling and keep them out of selection.\n"
        )
    present = decision.get("original_candidate_present", {})
    included = ", ".join(s for s, exists in present.items() if exists)
    absent = ", ".join(s for s, exists in present.items() if not exists)
    notes = (
        "Coverage criteria were declared before the census in v1: >=99.5% "
        "valid canonical full-hour coverage, no missing entire aligned sessions, "
        "max2consecutive scheduled missing hours, no invalid/duplicate rows. "
        "V2 excludes explicit issuer-history cautions after the initial census; "
        "v3 reserves126complete regular sessions rather than126calendar sessions. "
        "this conservative clarification is disclosed, with no return/model "
        "criterion. The longest month-boundary interval wins, latest end on ties. "
        "Then use publisher-sector ETF round robin, missingness and alphabetical "
        "ties. The publisher large-cap claim is a broad unverified liquidity "
        "proxy. This surviving-symbol/history-quality selection is retrospective, "
        "not PIT membership, sector or issuer certification.\n"
    )
    (out / "stock_universe_shortlist.md").write_text(
        "# Hourly universe shortlist\n\n"
        + shortlist
        + "\n"
        + notes
        + f"\nOriginal candidate names present: {included}; absent: {absent}. "
        + "See hourly_symbol_census.csv, hourly_coverage_by_year.csv and "
        + "per_symbol_coverage.json for ranges and denominators.\n\n"
        + chronology
    )
    template = Path(__file__).resolve().parents[2] / "docs/track_a/templates"
    text = (template / "hf_hourly_source_suitability.md").read_text()
    (out / "source_suitability_and_rights.md").write_text(
        text.replace("{{SOURCE}}", source).replace("{{CARD}}", card)
    )
    acquisition = (
        f"Dataset: twelvedata/financial-world-model, bars_1h, revision `{revision}`. "
        f"Three files, {sum(r['bytes'] for r in manifest['files']):,}bytes; "
        f"{quality['rows']:,}rows / {quality['symbols']}symbols.\n\n"
    )
    strict = (
        f"Original2020–2024 calendar-only qualifying names: "
        f"{decision['strict_calendar_qualifying_count']}; with required "
        f"prehistory: {decision['strict_with_required_prehistory_qualifying_count']}. "
        "STRICT_COMPATIBLE is false. Source/adjustment/rights and original "
        "native30-minute lineage are not cleared by row coverage.\n\n"
    )
    next_action = (
        "Decide whether to authorize a separate hourly-native methodology and "
        "rights-resolution study for the conditional cohort, or hold this source "
        "and separately authorize the named1-minute fallback pilot. No training, "
        "D1/TG0/frozen-split migration, pair expenditure or original confirmation "
        "access is authorized. PIT action/volume parity, dividends, historical "
        "available_at and modeling/redistribution permission remain UNVERIFIED. "
        "Ledger stays28/200.\n"
    )
    decision_text = (
        "**"
        + " / ".join(decision["flags"])
        + "**\n\n"
        + acquisition
        + shortlist
        + "\n"
        + chronology
        + "\n"
        + strict
        + next_action
    )
    (out / "NEXT_DECISION.md").write_text("# Next researcher decision\n\n" + decision_text)
    (out / "human_review_card.md").write_text(
        "# Hourly source human review\n\n"
        + decision_text
        + "\nInspect the clock transition, early-close/DST grid, close_adj fallback "
        + "and action-boundary/overlap ratios. These are source diagnostics, "
        + "not a vendor-truth or price-executability certificate.\n"
    )
    write_json(
        out / "report_bindings.json",
        dict(
            revision=revision,
            acquisition_manifest=dict(
                path=str(out / "acquisition_manifest.json"),
                sha256=digest(out / "acquisition_manifest.json"),
            ),
            config=dict(path=str(config_path), sha256=digest(config_path)),
            source=source,
            card=card,
            rights="https://twelvedata.com/terms",
            original_model_pairs=28,
            original_confirmation_access=False,
            training=False,
        ),
    )
