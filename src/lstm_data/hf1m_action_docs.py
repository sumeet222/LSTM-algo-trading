"""Publish the evidence-derived P019B register and bounded pre-feature release."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from .hf1m_action_audit import SYMBOLS, digest
from .hf1m_action_source import NAMESPACE, publish_json


def table(columns: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    """Small Markdown table; never pass proprietary OHLCV values."""

    def cell(value: object) -> str:
        return str(value).replace("|", "/").replace("\n", " ")

    return (
        "\n".join(
            ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
            + ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]
        )
        + "\n\n"
    )


def write_new(path: Path, body: str) -> None:
    """Allow identical replay, reject silently replacing any published document."""
    if path.parent != Path("."):
        body = re.sub(
            r"\]\((reports/[^)]+)\)",
            lambda match: "](" + Path(os.path.relpath(match[1], path.parent)).as_posix() + ")",
            body,
        )
    if path.exists():
        if path.read_text() != body:
            raise ValueError(f"DOCUMENT_ALREADY_PUBLISHED: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(body)
    temporary.replace(path)


def publish(out: Path) -> None:
    """Require complete reconciled evidence, then emit narrative and SHA-bound gate."""

    def read(name: str):
        return json.loads((out / name).read_text())

    events = read("unresolved_event_ledger_v3.json")
    summary = read("candidate_origin_summary_v2.json")
    release = read("action_disposition_release.json")
    independent = read("independent_reconstruction_receipt.json")
    split = read("split_boundary_proof.json")
    if (
        len(events) != 69
        or len({e["event_id"] for e in events}) != 69
        or release["uncontrolled_remaining"] != 0
        or independent["result"] != "PASS"
        or split["count"] != 9
    ):
        raise ValueError("STOP_REGISTER_INCOMPLETE")
    unresolved = [e for e in events if not e["disposition"].startswith("VERIFIED_")]
    if {e["event_id"] for e in unresolved} != {f"P019-{i:03d}" for i in range(1, 47)}:
        raise ValueError("STOP_REGISTER_INCOMPLETE: original 46 IDs differ")
    hours = pd.read_csv(out / "event_to_hour_dependency_v2.csv")
    origins = pd.read_csv(out / "event_to_origin_dependency.csv")
    counts = summary["counts"]
    root = Path("UNRESOLVED_MARKET_DATA_ANOMALIES.md")
    prefix = out.as_posix()

    def link(name: str) -> str:
        return f"[{name}]({prefix}/{name})"

    status = "PRE_FEATURE_READY_WITH_QUARANTINES"
    identity = (
        f"**{status} — source and availability masks only.** As of 2026-10-22. "
        f"Namespace `{NAMESPACE}`; exclusively `mito0o852/OHLCV-1m`, immutable revision "
        "`776328445b7ac6e7815ef3a483e9c8ded1eb6d56`, July 1, 2010–March 31, 2026. "
        "Four-hour same-session endpoint potential; no returns or targets calculated.\n\n"
        + "Canonical order: "
        + ", ".join(SYMBOLS)
        + ". All 20 retained.\n\n"
        "Rights: `HUMAN_REPORTED_MAINTAINER_PERMISSION_FOR_PRIVATE_RESEARCH`; "
        "not independent legal certification. Raw prices and detailed "
        "price examples remain local/ignored. "
        "UNRESOLVED means evidence does not establish an exact "
        "interpretation or price treatment; "
        "it does not mean fraud or that prices are fabricated.\n\n"
    )
    source = (
        "The correction implementation is `configs/hf1m_action_qa_v1.json` and "
        "`src/lstm_data/hf1m_action_source.py`, with boolean dependencies in "
        "`hf1m_action_masks.py` and closure/independent reconstruction in "
        "`hf1m_action_release.py`. "
        "The original execution snapshot and explicit compatibility "
        "amendment preserve code lineage; "
        "the source manifest retains the original execution SHA, not a "
        "falsely substituted final SHA.\n\n"
        "Original allowlist: [018D complete "
        "manifest](reports/data_audit/ta018d_hf1m_long_2026-10-22_155547/c"
        "omplete_acquisition_manifest.json), "
        "SHA256 `2b8f9165b0387acaf650d1f1514afb8b41d081aacc9b2056b2f6efa496adf40c`. "
        "All 1,701 exact active raw/QA files are checked by path, size and SHA; "
        "no physical-root discovery, pre-July2010 processing, legacy data "
        "fallback or new OHLCV acquisition. "
        "Every event's raw row ID below joins its full path and full file "
        "SHA in the current ledger. "
        "A short SHA below is an index, not the full identity.\n\n"
    )
    reconciliation = (
        "## Count reconciliation\n\n"
        + table(
            ["Disposition", "Candidate minutes", "Canonical ticker/date groups"],
            [
                [
                    kind,
                    number,
                    len({e["canonical_event_id"] for e in events if e["disposition"] == kind}),
                ]
                for kind, number in sorted(Counter(e["disposition"] for e in events).items())
            ],
        )
        + (
            "Original 67 = 17 split candidate minutes (9 actions) + 4 genuine "
            "moves + 46 policy-handled candidates. "
            "The RTH-only rescan exposed two additional genuine earnings "
            "gaps, so final 69 = 17 + 6 + 46. "
            "The 46 original blocker IDs remain exactly P019-001…P019-046: 18 "
            "RTH suspect minutes, "
            "24 EH records, 3 KO EH records and 1 COP boundary. They "
            "represent 24 ticker/date policy groups, "
            "not 46 unique RTH candles removed. Multiple flags/rows at one "
            "timestamp merge under one event ID; "
            "same-date groups list every alias below.\n\n"
            "The 18 RTH minutes affect 14 distinct bins (11 full hours, 3 closing stubs). "
            "Their independently genuine scheduled closes remain usable. COP "
            "adds one direct boundary "
            "and 806 full-hour feature-history dependencies. Origin "
            "dependency union is 401 unique scheduled "
            "origins: 133 OHLC contexts plus 268 COP price-basis contexts. "
            "These footprints are not 401 new "
            "joint admission losses: other defects overlap. COP removes 142 "
            "otherwise jointly available "
            "training origins (5,352→5,210); RTH extreme-minute removal "
            "causes zero extra genuine future-endpoint "
            "losses. EH/KO excludes no RTH hours or origins.\n\n"
        )
    )
    policy = (
        "## Applied policy and causal scope\n\n"
        "UTC nanosecond minute starts are preserved; ET uses America/New_York with DST. "
        "XNYS open-anchored full hours and separate closing stubs retain "
        "the complete scheduled grid; "
        "missing positions are never compressed. All EH rows are excluded "
        "before aggregation, prior-close "
        "anchors, gaps and factor application. No past-session close can "
        "fill an opening minute.\n\n"
        "Verified splits adjust the entire earlier OHLC segment by the "
        "reciprocal of every later verified "
        "split, composed through March2026. This is an ex-post unit "
        "convention, not PIT price availability. "
        "Future feature code must use origin-basis factors or "
        "scale-invariant representations. "
        "Observed share volume remains as reported; no inverse split "
        "factor is justified, and "
        "`volume_basis_id` plus `origin_volume_history_basis_consistent` "
        "expose regime crossings. "
        "No dividend or COP distribution factor, replacement vendor "
        "price, clipping or smoothing is used.\n\n"
        "All five fields of each suspect RTH minute are excluded. "
        "Independent scheduled first/last "
        "genuine-minute open/close survive where present. High/low are "
        "marked untrusted and set missing "
        "in affected bins; remaining observed extrema are private QA "
        "only. Observed-volume sums exclude "
        "quarantined prints and remain incomplete, never measured zero by "
        "imputation. True observed zeros "
        "survive. Existing 018D causal price-only cap5 proxies may "
        "support input-close continuity, "
        "but never label endpoints. No proxy is used anywhere in an "
        "anomaly-containing bin or across "
        "opening/session/action discontinuities; unknown volume remains unknown.\n\n"
        "Hour columns include `genuine_open`, `genuine_close`, "
        "`hour_usable_price_endpoints`, "
        "`hour_field_usable_open/close/high/low` and "
        "`hour_field_usable_complete_volume`, `hour_proxy_price_usable`, "
        "`missing_count`, `conflict_count`, `proxy_count`, "
        "`quarantine_count`, `observed_volume_complete`, "
        "`untrusted_fields`, `anomaly_event_ids`, `price_basis_id`, "
        "`action_boundary` and the companion "
        "`hour_feature_dependency_action_crossing`. The private overlay "
        "contains masks, not replacement prices.\n\n"
        "Origin columns include `origin_input_48_cap0`, `origin_input_48_cap5`, "
        "`origin_input_48_eligible` (cap5 closing-price upper bound), "
        "`origin_input_ohlc48_potential`, "
        "`origin_volume48_complete`, `action_crossing_input`, "
        "`origin_future_4h_eligible` and "
        "`origin_cross_section_20_eligible`. Input masks use past-only "
        "availability plus structural "
        "126-regular-session/360-genuine-hour warmup; they do not compute "
        "any indicator. Future endpoint "
        "availability is separate and never changes input eligibility. "
        "Four-hour endpoints are genuine "
        "10:30→14:30 or 11:30→15:30 ET completed closes on six-full-hour "
        "sessions only; no stubs, "
        "overnight horizons or proxies. The two-minute issuance "
        "assumption is clock metadata, not "
        "certification of vendor publication latency.\n\n"
    )
    register = (
        "# Unresolved and excluded market-data anomalies\n\n"
        + identity
        + source
        + reconciliation
        + policy
    )
    explanations = {
        "UNVERIFIED_RTH_LOCAL_QUARANTINE": (
            "RTH extreme-minute records",
            "Material intraminute range exceeds the predeclared detector. "
            "Exact print/correction status "
            "and true extrema remain unknown; numerical implausibility is not proof of error. "
            "Exclude the minute and high/low/volume dependencies, retain "
            "independently verified endpoints.",
        ),
        "UNVERIFIED_EH_OUT_OF_SCOPE": (
            "Extended-hours records — OUT_OF_RTH_SCOPE",
            "Material EH range/body/adjacent-price or reversal flags remain unexplained. "
            "No EH observation enters RTH levels, anchors or factor "
            "calculations; zero RTH dependency impact. "
            "The general RTH rescan independently checks for persistence into "
            "the admitted basis.",
        ),
        "KO_MIXED_BASIS_PREMARKET": (
            "KO premarket mixed basis — OUT_OF_RTH_SCOPE",
            "All three records are on August13,2012 at 04:03,07:07,07:13 ET; "
            "their mixed source basis "
            "is unresolved. The confirmed 2-for-1 split is separate. Genuine "
            "RTH boundary close ratio "
            "0.4984139069 becomes 0.9968278139 after the verified factor, and "
            "RTH basis stays consistent. "
            "All premarket rows are excluded; no EH splice and no RTH quarantine is required.",
        ),
        "COP_2012_SPINOFF_LOCAL_BOUNDARY": (
            "COP 2012 distribution boundary",
            "The PSX spinoff is verified: one PSX share per two COP shares "
            "after April30 close. "
            "The observed new-side boundary is May1,2012 09:30 ET, not an "
            "assumed midnight event time. "
            "A coherent price-only/total-return adjustment remains "
            "unsupported; tax allocation is not "
            "an approved causal multiplier. Retain genuine levels and split "
            "price_basis_id PRE/POST. "
            "Block crossing returns and the explicit "
            "125-prior-regular-session anchor history plus "
            "48-step input context (806 full-hour dependencies; 268 origin "
            "contexts), not whole years. "
            "The same-day four-hour clocks do not cross the opening boundary. "
            "No PSX prices or invented factor.",
        ),
    }
    for kind, (heading, explanation) in explanations.items():
        register += f"## {heading}\n\n{explanation}\n\n"
        rows = []
        subset = [e for e in unresolved if e["disposition"] == kind]
        for event in subset:
            hd = hours.loc[hours.event_id.eq(event["event_id"])]
            od = origins.loc[origins.event_id.eq(event["event_id"])]
            rows.append(
                [
                    event["event_id"],
                    event["ticker"],
                    event["timestamp_utc"],
                    event["timestamp_et"],
                    ",".join(event["rules"]),
                    event["raw_record_id"],
                    event["raw_linkage_hash"][:12],
                    ",".join(event.get("actual_containing_rth_hour_ids", [])) or "EH: none",
                    f"{hd.hour_id.nunique()} / {od.origin_id.nunique()}",
                ]
            )
        register += table(
            [
                "Event ID",
                "Stock",
                "UTC",
                "ET",
                "Original reason",
                "Raw row ID",
                "File SHA prefix",
                "Direct RTH bin",
                "Dependent hours / origins",
            ],
            rows,
        )
        register += "Canonical groups (all aliases):\n\n"
        register += table(
            ["Canonical group", "Candidate aliases"],
            [
                [
                    group,
                    ", ".join(e["event_id"] for e in subset if e["canonical_event_id"] == group),
                ]
                for group in sorted({e["canonical_event_id"] for e in subset})
            ],
        )
    register += "## Impact by stock and event year\n\n"
    impact_rows = []
    for stock, year in sorted({(e["ticker"], e["timestamp_et"][:4]) for e in unresolved}):
        chosen = [e for e in unresolved if e["ticker"] == stock and e["timestamp_et"][:4] == year]
        ids = {e["event_id"] for e in chosen}
        impact_rows.append(
            [
                stock,
                year,
                len(chosen),
                sum(e["disposition"] == "UNVERIFIED_RTH_LOCAL_QUARANTINE" for e in chosen),
                hours.loc[hours.event_id.isin(ids), "hour_id"].nunique(),
                origins.loc[origins.event_id.isin(ids), "origin_id"].nunique(),
            ]
        )
    register += table(
        [
            "Stock",
            "Event year",
            "Policy IDs",
            "RTH minutes removed",
            "Dependent hours (union)",
            "Dependent origins (union)",
        ],
        impact_rows,
    )
    register += (
        "Year here means event year; machine origin dependencies carry "
        "their actual origin dates. "
        "Do not sum overlapping alias footprints. Routine "
        "missing/conflict observations are not material "
        "jump exclusions. The checked 018D register records 279,180 "
        "absent RTH stock-minutes and "
        "406 conflicting timestamp keys / 856 raw rows (328 RTH keys, 78 "
        "EH keys). Conflicts are never "
        "resolved by first/last selection. Original 226,423 cap5 proxies "
        "are sensitivity records, not genuine prints. "
        "The new per-stock/year table retains missing, conflict, proxy, "
        "quarantine, genuine-close and "
        "volume-completeness counts separately: " + link("stock_year_hour_quality.csv") + ".\n\n"
    )
    facts = json.loads(Path("configs/hf1m_p019_verified_event_facts_v1.json").read_text())["events"]
    supplement = json.loads(Path("configs/hf1m_action_qa_supplement_v1.json").read_text())
    resolved = "## Resolved context — not unresolved exclusions\n\n"
    resolved += table(
        ["Stock/date", "Treatment", "Candidate IDs", "Public evidence (accessed 2026-10-22)"],
        [
            [
                f"{f['ticker']} {f['date']}",
                f"{f['factor_denominator']}:1 split; entire prior OHLC segment"
                if f["kind"] == "SPLIT"
                else "Genuine economic move retained; factor1",
                ", ".join(
                    e["event_id"]
                    for e in events
                    if e["ticker"] == f["ticker"]
                    and e["timestamp_et"][:10] == f["date"]
                    and e["disposition"].startswith("VERIFIED_")
                ),
                "; ".join(f"[{s['title']}]({s['url']})" for s in f["sources"]),
            ]
            for f in facts
            if f["kind"] in {"SPLIT", "MARKET_MOVE"}
        ]
        + [
            [
                f"{f['ticker']} {f['date']}",
                "New RTH-only earnings gap retained; factor1",
                f["event_id"],
                "; ".join(f"[{s['title']}]({s['url']})" for s in f["sources"]),
            ]
            for f in supplement["events"]
        ],
    )
    resolved += (
        "The two new RTH-only opening gaps are TSLA May9,2013 following "
        "May8's first profitable quarter "
        "and AMD October25,2018 following October24's earnings/outlook "
        "release. Their four raw "
        "before/after endpoints matched canonical rows exactly; no new "
        "quarantine was added. "
        "The initial post-adjustment receipt retains their provisional "
        "flags; the append-only "
        "`action_disposition_release.json` resolves them before final masks. "
        "The current v3 ledger updates activated metadata; v2 retains the "
        "detection closure and same69IDs.\n\n"
    )
    register += resolved
    coverage = (
        "## Coverage and proposed chronology\n\n"
        + table(
            [
                "Window",
                "Scheduled",
                "Genuine future20",
                "Input20 cap0 / joint",
                "Input20 cap5 / joint",
                "Before joint5",
                "OHLC joint",
                "Complete volume48 joint",
            ],
            [
                [
                    name,
                    c["schedule_origins"],
                    c["future20"],
                    f"{c['input20_cap0']} / {c['joint20_cap0']}",
                    f"{c['input20_cap5']} / {c['joint20_cap5']}",
                    c["before_joint20_cap5"],
                    c["ohlc_joint20"],
                    c["complete_volume48_joint20"],
                ]
                for name, c in counts.items()
            ],
        )
        + (
            "Proposed quality-only research span April1,2011–March31,2026 (15 "
            "calendar years), with "
            "July2010–March2011 startup history. Proposed training "
            "April2011–June2025 (14 years 3 months), "
            "development July–December2025, protected January–March2026. "
            "These are count filters/proposals, "
            "not materialized splits. Protected raw quality was inspected; no "
            "model outcome was accessed. "
            "Window/cohort choice is retrospective and survivorship "
            "conditioned, not PIT membership.\n\n"
            f"Training cap5 joint retention is {5210 / 7104:.4%}; development {194 / 250:.4%}. "
            "Sequential training loss decomposition: 7,104 scheduled→6,258 "
            "all20 past-input availability "
            "(846 fail warmup/past missingness/basis guard)→5,210 also "
            "genuine all20 future endpoints "
            "(1,048 further failures). Development 250→250→194 (56 endpoint failures). "
            "Before-action counts are unsafe presence-only diagnostics, never "
            "an admissible training source.\n\n"
            "These 5,210/194 origins are closing-price availability upper "
            "bounds, **not final 16-channel "
            "FT admission**. Strict OHLC joint potential is only 308 training /35 development; "
            "there is no complete 48-step volume window across all20. Long "
            "daily-indicator validity, "
            "channel missingness, volume regime handling and any train-fitted "
            "fallback require a separately "
            "approved feature implementation. Do not invent volume, silently "
            "drop channels or loosen rules "
            "to promote these upper bounds to FT-ready counts.\n\n"
            "Weakest training-coverage names are MA and AVGO. Hypothetically "
            "excluding AVGO gives "
            "5,533 joint origins; MA 5,540; both 5,885, versus all20 5,210. "
            "These are quality-only "
            "counterfactual counts, not a changed cohort or smaller TG. All20 "
            "remain mandatory. " + link("weak_stock_counterfactuals_v2.csv") + ".\n\n"
            "Exact stock/year before/after input and endpoint counts: "
            + link("stock_year_candidate_counts_v2.csv")
            + "; annual joint counts: "
            + link("yearwide_candidate_counts_v2.json")
            + ".\n\n"
        )
    )
    register += coverage
    bound_names = [
        "unresolved_event_ledger_v3.json",
        "unresolved_event_ledger_v3.csv",
        "canonical_event_ledger_pointer.json",
        "event_to_hour_dependency_v2.csv",
        "event_to_origin_dependency.csv",
        "hour_field_mask_manifest.json",
        "candidate_origin_summary_v2.json",
        "adjusted_hourly_manifest.json",
        "active_input_hash_receipt.json",
        "action_disposition_release.json",
        "split_boundary_proof.json",
        "independent_reconstruction_receipt.json",
        "source_execution_amendment_v2.json",
        "stock_year_hour_quality.csv",
        "stock_year_candidate_counts_v2.csv",
        "yearwide_candidate_counts_v2.json",
    ]
    register += "## Machine-readable evidence bindings\n\n" + table(
        ["Artifact", "SHA256"], [[link(name), digest(out / name)] for name in bound_names]
    )
    register += (
        "The current ledger is v3; unversioned/v2 files are preserved "
        "predecessors. Current hour "
        "dependencies are v2; origin/mask summaries are v2 where "
        "versioned. Companion manifests bind "
        "private field/origin Parquets by exact path, byte count and SHA. "
        "The gate JSON binds this "
        "root document's SHA (no self-hash cycle). Original 019 STOP "
        "reports remain unchanged.\n\n"
        "## Dated disposition and next human decision\n\n"
        f"**2026-10-22 — {status}.** Signed: Codex, execution of the user's Package019B "
        "localized-quarantine authority. This releases immutable "
        "source/QA masks for independent review, "
        "not legal certification, final-feature admission or permission "
        "to train. Nine splits applied, "
        "six genuine moves retained, all46 original policy IDs accounted "
        "for; no uncontrolled material "
        "candidate remains under the declared detector and evidence "
        "policy. Detector coverage is not "
        "proof every source error is absent.\n\n"
        "Future feature computation must load the current quarantine, "
        "field, action and origin masks "
        "and prove indicator-specific causal dependencies, origin-safe "
        "price units, unknown-volume "
        "handling and final all20 retention. Separately authorize that "
        "work and freeze the proposed "
        "chronology before any feature/target calculation or model "
        "selection. Publication timing, "
        "dividends and volume adjustment remain unverified. Research "
        "ledger remains32/200; no FT/TG, "
        "scalers, inference, training, trading, held-out outcomes or Git "
        "index/commit/push operations.\n"
    )
    write_new(root, register)
    write_new(
        out / "P019B_CORPORATE_ACTION_ACTIVATION.md",
        "# P019B corporate-action activation\n\n"
        + identity
        + source
        + resolved
        + "\n"
        + link("split_boundary_proof.json")
        + " verifies all9 directions/compositions and unchanged "
        "observed-volume sums. Independent67-hour reconstruction passed; "
        "full189-month checks conserve grid and endpoints.\n",
    )
    write_new(
        out / "P019B_QUARANTINE_POLICY_AND_COVERAGE.md",
        "# P019B quarantine policy and coverage\n\n"
        + identity
        + reconciliation
        + policy
        + coverage
        + "[Full root register](../../../UNRESOLVED_MARKET_DATA_ANOMALIES.md).\n",
    )
    decision = (
        "# P019B pre-feature gate decision\n\n"
        + identity
        + "All six source-release conditions are supported: all9 splits "
        "verified/applied; every69candidate "
        "disposition is traceable; rescan provisional gaps resolved "
        "without price edits; substantial "
        "closing-price all20 potential remains; allowlists/masks are "
        "immutable and reproducible; "
        "past inputs never use future endpoint availability. Source "
        "release is warranted with localized "
        "quarantines. The strict OHLC/volume envelope is marginal and "
        "does not pass final16-feature admission. "
        "Stop here for independent review and a separate feature-methodology prompt.\n\n"
        + coverage
        + "[Root anomaly "
        "register](../../../UNRESOLVED_MARKET_DATA_ANOMALIES.md). No "
        "automatic model authorization.\n"
    )
    write_new(out / "P019B_PRE_FEATURE_GATE_DECISION.md", decision)
    write_new(
        out / "human_review_card.md",
        "# P019B human review card\n\n"
        + identity
        + "9 split actions/17candidate minutes adjusted;6 genuine moves "
        "retained (4prior+2new);46 policy IDs dispositioned:18RTH "
        "quarantined,24EH+3KO outofRTH,1COP "
        "boundary.18minutes→14bins;401unique origin dependency "
        "footprints;142 incremental joint training origins excluded by "
        "COP.\n\n" + coverage + "[Root register](../../../UNRESOLVED_MARKET_DATA_ANOMALIES.md). "
        "Next action: independently review masks and authorize a separate "
        "feature task. Ledger32/200; no fits.\n",
    )
    write_new(
        out / "REPRODUCTION.md",
        "# Reproduction\n\nUse the repository authoritative .venv setup and "
        "exact active018D allowlist; no new credentials or downloads. "
        "From repository root, inspect the registered code/config/input "
        "SHAs before running. Reusing this sealed packet verifies "
        "completed checkpoints; a full new derivation must use a NEW "
        "--out directory and reproduce the documented discovery/closure "
        "order.\n\n```bash\n.venv/bin/python -B -m "
        "lstm_data.hf1m_action_source --out "
        + prefix
        + "\n.venv/bin/python -B -m lstm_data.hf1m_action_release "
        "--prepare-events --boundary-proofs --out "
        + prefix
        + "\n.venv/bin/python -B -m lstm_data.hf1m_action_masks --out "
        + prefix
        + "\n.venv/bin/python -B -m lstm_data.hf1m_action_release "
        "--finalize-fields --verify-samples --out "
        + prefix
        + "\n.venv/bin/python -B -m lstm_data.hf1m_action_docs --out "
        + prefix
        + "\n.venv/bin/python -m pytest tests/test_hf1m_action_source.py "
        "tests/test_hf1m_action_audit.py tests/test_hf_minute_long.py "
        "-q\n```\n\nThe final mask CLI emits v2 files and refuses unresolved "
        "scan candidates. Root-register publishing refuses replacement "
        "with different content; preserve this root and generate a "
        "separately named successor for any changed evidence. "
        "Price-bearing Parquets and trusted-local compact pickle "
        "checkpoints stay ignored. Never load untrusted pickles. Source "
        "checkpoint replay uses the explicit code-compatibility "
        "amendment; full new runs bind current code directly. Public URLs "
        "establish event facts, not vendor-feed certification. No FT/TG "
        "or training command is part of this procedure.\n",
    )
    bindings = {name: digest(out / name) for name in bound_names}
    publish_json(
        out / "pre_feature_gate.json",
        {
            "status": status,
            "as_of": "2026-10-22",
            "namespace": NAMESPACE,
            "root_register": {"path": str(root), "sha256": digest(root)},
            "evidence_sha256": bindings,
            "canonical_candidate_minutes": 69,
            "original_policy_ids": [e["event_id"] for e in unresolved],
            "source_only": True,
            "final16_feature_admission": False,
            "features_targets_training_authorized": False,
            "ledger": "32/200",
            "uncontrolled_candidates": 0,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    publish(parser.parse_args().out)


if __name__ == "__main__":
    main()
