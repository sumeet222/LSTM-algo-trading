"""One-shot reproducible Package009 report export; no fitting or source mutation."""

import argparse
import csv
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from lstm_data.config import digest
from lstm_data.wf2_replication import journal_rows, reference

parser = argparse.ArgumentParser(
    description=(
        "Create Package009 narrative and derived scalar tables from a "
        "completed, reviewed packet; refuses output overwrite."
    )
)
parser.add_argument("--package", type=Path, required=True)
args = parser.parse_args()
p = args.package
began = time.monotonic()
now = datetime.now(ZoneInfo("America/New_York"))


def read(f):
    return json.loads(f.read_text())


def put(n, value):
    with (p / n).open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")


def md(n, s):
    with (p / n).open("x") as f:
        f.write(s)


def csvout(n, rows):
    with (p / n).open("x", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def table(head, rows):
    return (
        "| "
        + " | ".join(head)
        + " |\n|"
        + "|".join("---" for _ in head)
        + "|\n"
        + "".join("| " + " | ".join(map(str, r)) + " |\n" for r in rows)
    )


s = read(p / "review_summary.json")
m = s["metrics"]
h = s["health"]
r = s["runtimes"]
pre = read(p / "preflight_and_bindings.json")
exe = read(p / "execution_summary.json")
rows = journal_rows(Path("reports/audit/track_a_real_pairs_v3.jsonl"))
assert exe["completed_pairs"] == 2 and len(rows) == 8
fit_table = table(
    ["Model", "WF2 MSE", "Daily Rank IC", "Cal/refit epochs", "Fit seconds", "G6"],
    [
        [
            n,
            f"{m[n]['MSE']:.9f}",
            f"{m[n]['daily_Rank_IC']:.9f}",
            f"{r[n]['calibration_epochs']}/{r[n]['refit_epochs']}",
            f"{r[n]['neural_fitting_seconds']:.3f}",
            h[n]["status"],
        ]
        for n in ("TM0", "MC0")
    ],
)
paired = pd.read_csv(p / "paired_daily_monthly.csv")
assoc = pd.read_csv(p / "batch_association_summary.csv")
dm = m["MC0"]["MSE"] - m["TM0"]["MSE"]
di = m["MC0"]["daily_Rank_IC"] - m["TM0"]["daily_Rank_IC"]
cons = {
    "MC0_lower_MSE_days": int((paired.MC0_minus_TM0_MSE < 0).sum()),
    "MC0_higher_IC_days": int((paired.MC0_minus_TM0_IC > 0).sum()),
    "IC_tied_days": int((paired.MC0_minus_TM0_IC == 0).sum()),
    "sessions": len(paired),
}
put("paired_consistency.json", cons)
headline = (
    f"ZERO WF2 MSE {m['ZERO']['MSE']:.9f}; project-conventional IC 0, "
    f"defined-only IC N/A. Exact common panel: 232 origins, 116 "
    f"sessions, 1160 stock forecasts, AAPL/COST/CMCSA/SBUX/CME, two "
    f"origins per day. Neither arm has extra attrition. MC0−TM0 ΔMSE "
    f"{dm:+.9f}; Δdaily IC {di:+.9f}. MC0 has lower MSE on "
    f"{cons['MC0_lower_MSE_days']}/116 days and higher IC on "
    f"{cons['MC0_higher_IC_days']}/116 ({cons['IC_tied_days']} ties)."
)
qual = (
    "ASSUMPTION_CONDITIONAL candidate preparation/pilot evidence: "
    "idealized zero-latency completed-hour period-end clock; "
    "retrospective split-price/inverse-volume representation and five "
    "surviving stocks; researcher-attested local stock/SPY "
    "rights/shared clock with private evidence uninspected; "
    "completed-hourly-close label proxy, not executable fills. SPY is "
    "an ETF state proxy, with no certified course USA500 substitution. "
    "No independent license, observed publication, action-vintage or "
    "PIT-universe certification. No redistribution authority. "
    "Production D1/CURRENT_PROTOCOL and confirmation outcomes remain "
    "unchanged."
)
epoch_rows = []
health_lines = []
for name in ("TM0", "MC0"):
    cal = [read(f) for f in sorted((p / name).glob("calibration_epoch_*.json"))]
    ref = [read(f) for f in sorted((p / name).glob("refit_epoch_*.json"))]
    selected = r[name]["refit_epochs"]
    for stage, trace in [("CALIBRATION", cal), ("REFIT", ref)]:
        for i, z in enumerate(trace, 1):
            train = z["training"] if stage == "CALIBRATION" else z
            g = train["gradients"]
            v = z.get("validation", {}) if stage == "CALIBRATION" else {}
            sel = z.get("selection", {})
            epoch_rows.append(
                {
                    "model": name,
                    "stage": stage,
                    "epoch": i,
                    "training_MSE": train["mse"],
                    "inner_validation_MSE": v.get("mse"),
                    "qualifying_selected_epoch_so_far": sel.get("selected"),
                    "selected_checkpoint": stage == "CALIBRATION" and i == selected,
                    "steps": train["steps"],
                    "training_score_std": train["score_std"],
                    "preclip_p50": g["median"],
                    "preclip_p90": g["p90"],
                    "preclip_p95": g["p95"],
                    "preclip_p99": g["p99"],
                    "preclip_max": g["max"],
                    "clipped_batch_fraction": g["clipped_fraction"],
                    "nonfinite_count": g["nonfinite_count"],
                    "sustained_gt50pct_warning": g["sustained_clipping_warning"],
                }
            )
    selected_cal = cal[selected - 1]
    a = h[name]["warning_epochs"]
    first = {k: (v[0] if v else None) for k, v in a.items()}
    health_lines.append(
        (
            f"{name}: calibration stopped epoch {len(cal)}, selected qualifying "
            f"epoch {selected}; selected inner MSE "
            f"{selected_cal['validation']['mse']:.9f}; selector "
            f"{h[name]['selector']['status']}. First >50% clipping warning: "
            f"calibration {first['calibration']}, refit {first['refit']}; "
            f"selected calibration clipped fraction "
            f"{selected_cal['training']['gradients']['clipped_fraction']:.6f}; "
            f"final refit fraction "
            f"{ref[-1]['gradients']['clipped_fraction']:.6f}. Both-pass status "
            f"{h[name]['status']}; nonfinite gradients "
            f"{h[name]['nonfinite_gradient_count']}. Warning epochs: {a}."
        )
    )
    csvout(name + "/epoch_health_summary.csv", [z for z in epoch_rows if z["model"] == name])
    md(
        name + "/training_health.md",
        "# "
        + name
        + " actual training health\n\n"
        + health_lines[-1]
        + (
            "\n\nFull train/validation curves and norm p50/p90/p95/p99/max are "
            "in epoch_health_summary.csv and immutable per-epoch JSON. The "
            "refit uses a fresh model with empty optimizer state, same seed "
            "initialization, distinct full-prefix recipe and exactly the "
            "selected epoch count. Final checkpoint predictions were reloaded "
            "and verified over the full WF2 panel.\n"
        ),
    )
csvout("training_curves_and_health.csv", epoch_rows)
smallassoc = table(
    [
        "Model",
        "Stage",
        "Sensitivity",
        "N batches",
        "ρ loss/norm",
        "ρ target max/norm",
        "Clip fraction",
    ],
    [
        [
            z.model,
            z.stage,
            z.sensitivity,
            z.batches,
            f"{z.loss_vs_preclip_spearman:.6f}",
            f"{z.targetmax_vs_preclip_spearman:.6f}",
            f"{z.clip_fraction_norm_gt1:.6f}",
        ]
        for z in assoc.itertuples()
    ],
)
fore = pd.read_csv(p / "wf2_matched_predictions.csv")
tail = []
for name in ("TM0", "MC0", "ZERO"):
    y = fore.TG0.to_numpy()
    e = (fore[name].to_numpy() - y) ** 2
    tail.append(
        {
            "model": name,
            "partition": "WF2",
            "stocks": len(y),
            "abs_TG0_max": float(np.abs(y).max()),
            "abs_TG0_p95": float(np.quantile(np.abs(y), 0.95)),
            "abs_TG0_p99": float(np.quantile(np.abs(y), 0.99)),
            "target_fraction_abs_gt10": float((np.abs(y) > 10).mean()),
            "target_fraction_abs_gt20": float((np.abs(y) > 20).mean()),
            "loss_fraction_from_abs_target_gt10": float(e[np.abs(y) > 10].sum() / e.sum()),
            "loss_fraction_from_abs_target_gt20": float(e[np.abs(y) > 20].sum() / e.sum()),
        }
    )
csvout("wf2_target_loss_tails.csv", tail)
md(
    "training_clipping_and_loss_review.md",
    "# Actual WF2 training, clipping and loss review\n\n"
    + "\n\n".join(health_lines)
    + "\n\n"
    + smallassoc
    + (
        "\nThe sensitivity excludes the five batches with largest absolute "
        "target maxima in each model/stage; this rule was fixed before "
        "outcomes. Repeated observations of the same session over epochs "
        "and changing model weights make these pooled associations "
        "descriptive. Positive association identifies co-occurring batch "
        "properties; it does not identify individual examples as causes, "
        "establish a causal target-tail explanation, or authorize a "
        "target/loss/clip change. Detached summaries never replace the "
        "frozen MSE objective. No raw volatility denominator was "
        "reconstructed from TG0.\n\nThe selected epoch, complete stopping "
        "trace and both passes are retained even when warnings begin after "
        "checkpoint selection. A 100% clipping epoch is reported as WARN. "
        "Refit-only health cannot clear earlier calibration warnings. "
        "Weight/score stability evidence is limited to finite traces, "
        "preserved selected/final checkpoint identities, identical fresh "
        "initialization/empty optimizer and full frozen forecast replay; "
        "no hidden-state or optimizer-history attribution was attempted. "
        "See wf2_target_loss_tails.csv and loss_concentration.csv for "
        "target thresholds and session-loss concentration.\n\n"
    )
    + qual
    + "\n",
)
context = table(
    ["Fold", "TM0 MSE", "MC0 MSE", "ZERO MSE", "TM0 IC", "MC0 IC", "MC0−TM0 ΔMSE", "MC0−TM0 ΔIC"],
    [
        [
            "WF1",
            "5.438829600",
            "5.450865550",
            "5.427531844",
            ".034913793",
            "-.012068966",
            "+.012035950",
            "-.046982759",
        ],
        [
            "WF2",
            f"{m['TM0']['MSE']:.9f}",
            f"{m['MC0']['MSE']:.9f}",
            f"{m['ZERO']['MSE']:.9f}",
            f"{m['TM0']['daily_Rank_IC']:.9f}",
            f"{m['MC0']['daily_Rank_IC']:.9f}",
            f"{dm:+.9f}",
            f"{di:+.9f}",
        ],
    ],
)
md(
    "wf1_vs_wf2_context.md",
    "# Frozen WF1 context and WF2 development replication\n\n"
    + context
    + "\n"
    + headline
    + (
        "\n\nWF1 values are read-only references from Packages007/008; no "
        "historical baseline was refitted. WF2 uses a longer permitted "
        "training prefix and newly fitted normalizers/TG0 floor, so "
        "absolute losses across folds have different targets/populations "
        "and should not be interpreted as a fixed-label temporal change. "
        "Use each fold's own ZERO and paired arm contrast. Both folds have "
        "now been inspected for development. One seed, five stocks and two "
        "development folds cannot settle market-feature usefulness. "
        "Five-session paired block intervals in review_summary.json are "
        "exploratory, reuse the existing utility and are not full G8 or "
        "selection-adjusted significance.\n\n"
    )
    + qual
    + "\n",
)
md(
    "visualization_handoff.md",
    (
        "# Later visualization handoff — no app implemented\n\nAll links "
        "below refer to compact local review artifacts under this packet; "
        "transfer/redistribution remains separately unevidenced.\n\n- "
        "`wf2_matched_predictions.csv`: session, origin, symbol, TG0, TM0, "
        "MC0, ZERO, grade. Join by exact session/origin/symbol; 1160 rows. "
        "Display model scores and realized labels with labels clearly "
        "future-only.\n- `paired_daily_monthly.csv` and "
        "`paired_monthly.csv`: each model's MSE/IC and MC0−TM0 "
        "differences. `wf2_comparison.csv` gives matched denominator and "
        "score dispersion/ties.\n- `training_curves_and_health.csv`: "
        "model/stage/epoch, train MSE, validation MSE, qualifying "
        "selection, step counts, score std, norm p50/p90/p95/p99/max, "
        "clipped fraction and nonfinite count. Preserve both passes and "
        "mark selection separately from stop.\n- "
        "`batch_loss_vs_gradient.csv`: "
        "architecture/stage/epoch/batch/step, session IDs, effective "
        "session weights, MSE, preclip norm, multiplier, target "
        "max/p95/counts and largest session-loss share. Use log axes where "
        "appropriate; label repeated-epoch batch association as "
        "descriptive. `batch_association_summary.csv` supplies the fixed "
        "sensitivity summaries.\n- `wf2_target_loss_tails.csv` and "
        "`loss_concentration.csv`: target tails and session concentration, "
        "with actual denominator and partition.\n- `input_binding.json` "
        "and four new recipe JSONs: exact stock/market source IDs and "
        "retrospective transform metadata; `preparation_review.md` "
        "explains time boundaries and exclusions.\n\nA later "
        "candlestick/volume/indicator viewer should retrieve authorized "
        "local bars through the existing component/source APIs using these "
        "source IDs and exact UTC/Eastern session clocks. The compact "
        "prediction files do not contain OHLCV. Do not invent candles or "
        "raw/unadjusted prices from normalized channels. Closing stubs, "
        "split representation, source/ideal availability, feature value "
        "time and forecast/label horizon need distinct UI marks. Existing "
        "U1–U5 definitions and 16-channel stock feature metadata are "
        "linked through the recipes and component binding. The historical "
        "retrospective representation is available locally; PIT "
        "action/publication facts and executable minute fills remain "
        "uncertified. No raw archive, dense window store, vendor GET, "
        "Plotly/Streamlit app or redistribution bundle was created.\n"
    ),
)
# Protection and resources are measured independently from fit timing.
changes = {
    n: {"before": v, "after": digest(Path(n)) if Path(n).exists() else None}
    for n, v in pre["protected"].items()
    if not Path(n).exists() or digest(Path(n)) != v
}
allowed = set(pre["allowed_source_edits"]) | {
    "configs/CURRENT_EXPERIMENT_REGISTRY.json",
    "docs/track_a/RandomNotes.md",
}
assert not set(changes) - allowed, changes
pres = {
    "protected_count": len(pre["protected"]),
    "changed": changes,
    "unexpected_changes": [],
    "concurrent_external_note": "RandomNotes.md preserved without agent edits",
    "old_source_before_images_verified": all(
        digest(p / "historical_source" / (Path(n).name + ".txt")) == pre["protected"][n]
        for n in pre["allowed_source_edits"]
    ),
    "v1_unchanged": digest(Path("reports/audit/track_a_real_pairs_v1.jsonl"))
    == pre["protected"]["reports/audit/track_a_real_pairs_v1.jsonl"],
    "v2_unchanged": digest(Path("reports/audit/track_a_real_pairs_v2.jsonl"))
    == pre["protected"]["reports/audit/track_a_real_pairs_v2.jsonl"],
    "raw_old_components_weights_and_reports_unchanged": True,
    "current_registry": reference(Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")),
    "new_journal": reference(Path("reports/audit/track_a_real_pairs_v3.jsonl")),
    "new_event_count": len(rows),
    "starting_pairs": 4,
    "final_started_pairs": 6,
    "new_completed_pairs": 2,
    "ceiling": 40,
}
put("preservation_and_registry_audit.json", pres)
resource = {
    "package_started_at": pre["package_started_at"],
    "snapshot_at": now.isoformat(),
    "package_elapsed_seconds_at_snapshot": (
        now - datetime.fromisoformat(pre["package_started_at"])
    ).total_seconds(),
    "deadline": pre["deadline"],
    "report_reserve_seconds": 900,
    "actual_train_and_worker": r,
    "per_pair_supervisor": {
        n: read(p / n / "supervisor_actual_runtime.json") for n in ("TM0", "MC0")
    },
    "executions": {
        n: read(p / (n + "_command.json"))
        for n in (
            "batch_execution",
            "batch_execution_corrected",
            "batch_execution_absolute",
            "review",
        )
    },
    "prepared_recipe_compute": {
        k: read(p / "prepared_dataset_retention.json")[k]
        for k in ("stock_recomputation_seconds", "market_recomputation_seconds")
    },
    "all_logged_command_seconds": sum(read(f)["elapsed_seconds"] for f in p.glob("*_command.json")),
    ("timing_semantics"): (
        "Neural fitting is measured calibration_training+refit_training, "
        "including forward/backward/step and scalar telemetry overhead, "
        "excluding validation; not optimizer-kernel-only. Worker, "
        "supervisor, wrapper and entire package are distinct; parallel "
        "check durations must not be summed as package wall time."
    ),
}
put("resource_and_elapsed.json", resource)
checks = {
    "status": "PASS_SCOPED_WITH_G6_WARNINGS",
    "focused": "53 passed, one runpy entry-test RuntimeWarning; 12.03 seconds",
    "static": read(p / "static_entrypoint.txt")["summary"],
    "ruff": "PASS",
    "git_diff_check": "PASS",
    "telemetry_equivalence": reference(p / "telemetry_equivalence.json"),
    "corrected_old_approval_negative": "EXPECTED_REFUSAL_BEFORE_FIT",
    "final_reload": s["reload_verification"],
    "matched_panel": "232 origins/116 days/1160 forecasts, exact all-five targets",
    ("batch_conservation"): (
        "one row per optimizer step; each fit session exactly once per "
        "epoch; weighted MSE and clip fractions reconcile"
    ),
    "preservation": reference(p / "preservation_and_registry_audit.json"),
    ("editor_refresh"): (
        "Human confirmation pending; repository .venv, Pylance basic, refresh Problems."
    ),
    "full_legacy_suite": "Not run per bounded scope; no inherited result claimed as new.",
}
put("checks.json", checks)
nexts = (
    "1. Review the sealed WF2 packet, then request a separate "
    "visualization package using the compact handoff.\n2. If justified "
    "by this evidence, specify and approve one controlled "
    "target/loss/normalization experiment with fixed comparison and "
    "budget. Do not run it from this packet.\n3. Keep future seed/fold "
    "replication, finalist selection and economic/proxy accounting "
    "behind their own exact scopes; no automatic promotion or "
    "confirmation access.\n"
)
gates = (
    "G0: qualified researcher attestation and actual new approval, no "
    "independent rights/clock certification. G1: "
    "source/calendar/action uncertainty retained. G2: frozen TG0, "
    "feature and universe definitions retained. G3: matched genuine "
    "preparation passes under idealized assumptions. G4: development "
    "predictive comparison only, economic claims held. G5: "
    "longer-prefix fitting/purge/masks and new authority bound. G6: "
    "both-pass health warnings preserved. G7: no "
    "trading/cost/execution validation granted. G8: exploratory paired "
    "intervals only."
)
md(
    "human_review_card.md",
    (
        "# Package009 human review — "
        "COMPLETED\n\nTA009_WF2_TWO_PAIRS_COMPLETED. Two exact authorized "
        "TM0→MC0 pairs completed; ledger **4/40→6/40**, cap40 unchanged. "
        "No follow-on run is authorized.\n\n"
    )
    + fit_table
    + "\n"
    + headline
    + "\n\n"
    + context
    + "\n"
    + "\n\n".join(health_lines)
    + "\n\n"
    + qual
    + "\n\n"
    + gates
    + (
        "\n\nActual pair fit time is calibration+refit training wall time "
        "including observation; see resource_and_elapsed.json for distinct "
        "worker/supervisor/wrapper/package time. The two pre-start "
        "launcher failures consumed zero slots, are preserved, and are not "
        "fit retries. Corrected code received a new actual approval. Both "
        "old journals and historical weights remain unchanged. Final "
        "reload, matched masks and batch conservation pass; 53 focused "
        "tests and zero-error installed-extension analysis pass. No "
        "profitability or causal conclusion follows from batch "
        "correlations or one seed.\n\nNext options:\n\n"
    )
    + nexts,
)
md(
    "package_report.md",
    "# Package009 WF2 temporal replication — completed\n\n"
    + fit_table
    + "\n"
    + headline
    + (
        "\n\nThe exact two-pair scope and corrected execution code "
        "received an attributable live approval in "
        "authority_corrected.json, proposal "
        "b1ca944b79f9d01a2fca04094a22bf9c22434d5c85cbb05cd2434d250f93156a. "
        "authority.json is the earlier launcher approval, retained without "
        "extension. The full preparation, failed pre-start launch "
        "attempts, exact recipes and post-run diagnostics are preserved in "
        "this packet.\n\n"
    )
    + qual
    + (
        "\n\nRead human_review_card.md for the short decision packet, "
        "training_clipping_and_loss_review.md for both-pass health and "
        "batch associations, wf1_vs_wf2_context.md for fold contrasts, "
        "preparation_review.md for actual denominators and time semantics, "
        "commands.md for reproduction and visualization_handoff.md for a "
        "later app. Checkpoint hashes and fresh optimizer/initialization "
        "identity are verified in review_summary.json; all "
        "source/code/artifact hashes are in the inventories.\n\n"
    )
    + gates
    + "\n\n"
    + nexts,
)
# Session report is written before the inventory so it is inventoried too.
report = Path("reports/codex_sessions") / (
    now.strftime("%Y-%m-%d_%H%M%S") + "_ta009_wf2_replication.md"
)
status = subprocess.run(
    ["git", "status", "--short", "--branch"], capture_output=True, text=True, check=True
).stdout
(p / "git_status_final.txt").write_text(
    status + "\nSession report being created: " + str(report) + "\n"
)
sections = [
    (
        "1. Session metadata",
        (
            f"Date/time {now.isoformat()}, Codex root, no subagents. Task "
            f"Package009 exact WF2 TM0/MC0 replication. Branch {pre['branch']}. "
            f"Starting/ending HEAD {pre['HEAD']}; no commit. Startup fetch "
            f"PASS, ahead1/behind0, initial tree clean. No issue/PR. Current "
            f"uncommitted state in git_status_final.txt; concurrent external "
            f"RandomNotes.md edit preserved."
        ),
    ),
    (
        "2. Executive summary",
        (
            "TA009_WF2_TWO_PAIRS_COMPLETED; matched panel sealed; 4/40→6/40. "
            "Both passes independently audited.\n\n"
        )
        + fit_table,
    ),
    (
        "3. Research/protocol impact",
        (
            "Only approved longer fitting cutoff (December2023) and WF2 "
            "development evaluation (January–June2024), plus optional scalar "
            "observability. Target, horizon, channels, architecture, "
            "optimizer, loss, clip, seed, sampler, D6g selection, costs and "
            "universe unchanged. New independently recomputed inner/full "
            "recipes; no June recipe substituted. No confirmation or "
            "production change. P2 v1 16 entries hash-verified via "
            "load_deferred_work and authorized v4 successor read; no "
            "status/pointer changed or global scientific closure asserted."
        ),
    ),
    (
        "4. Files created",
        (
            f"New modules src/lstm_data/batch_telemetry.py, wf2_replication.py, "
            f"wf2_review.py; tests/test_wf2_replication.py; "
            f"docs/track_a/WF2_Replication_009_API.md; "
            f"configs/track_a_candidate_experiment_registry_v3.json; "
            f"reports/audit/track_a_real_pairs_v3.jsonl; packet {p}; this "
            f"report. artifact_inventory.csv itemizes each new file's "
            f"type/size/hash and purpose. Generated checkpoint files are "
            f"intentionally local and gitignored."
        ),
    ),
    (
        "5. Files modified",
        (
            "src/lstm_data/real_batch_data.py adds WF2 fold to existing "
            "indexed views; real_bridge_authority.py admits exact sealed WF2 "
            "authority; real_bridge_run.py adds optional observer and "
            "fold-aware dispatch/resource projection without duplicating the "
            "numerical loop. CURRENT_EXPERIMENT_REGISTRY.json activates "
            "approved linked v3 at actual STARTED. RandomNotes.md is a "
            "concurrent external modification, never edited here. Three "
            "original source before-images are archived and hash verified."
        ),
    ),
    (
        "6. Files deleted, renamed, or moved",
        (
            "No preexisting/raw/human file deleted or moved. Own failed-launch "
            "execution_summary.json moved to "
            "entrypoint_attempt1/execution_summary_original.json, with an "
            "earlier identical snapshot also retained. Own empty/pre-start TM0 "
            "namespace containing only supervisor runtime moved to "
            "attempt2_relative_output/TM0. Failed preparation metadata "
            "archived under prepare_attempt1_timestamp_metadata. Prior exact "
            "source snapshots are retained; nothing discarded."
        ),
    ),
    (
        "7. Critical interfaces",
        (
            "WF2PairAuthority.ensure/view/append; authority factory binds new "
            "concrete approval/code/input/fold and linked journal. "
            "BatchInputs.fold defaults WF1 and selects WF2 only for new "
            "authority. epoch_pass optional batch_sink observes detached "
            "loss/single preclip return after the existing optimizer step. "
            "BatchTelemetry.record writes one scalar row per effective batch, "
            "no RNG/autograd/optimizer changes. wf2_review performs final-only "
            "inference, exact matched targets, conservation and descriptive "
            "paired analysis. Full signatures/invariants in "
            "WF2_Replication_009_API.md."
        ),
    ),
    (
        "8. Data/schema/provenance changes",
        (
            "No raw source schema changes. New immutable stock/market recipe "
            "JSONs and source-linked compact CSVs; 813 inner, 54 validation, "
            "875 full-refit, 116 WF2 sessions with 2 origins/5 stocks. "
            "Calendar tail October2–December2023 fixed; 16 ASOF origins "
            "excluded at validation and WF2. Historical cutoff and actual "
            "recipe-construction clocks distinguished; no future labels in "
            "inputs. "
        )
        + qual,
    ),
    (
        "9. Dependency/environment changes",
        (
            "None. Existing .venv and declared Torch/NumPy/Pandas only. CPU "
            "float32, Torch1 thread; OMP/OPENBLAS/MKL/VECLIB caps1. Installed "
            "Pylance basic parity unchanged. No installation, "
            "credential/private-email/vendor access or new source download."
        ),
    ),
    (
        "10. Commands and tests run",
        (
            "Exact commands/logs in *_command.json and commands.md. Focused "
            "pytest: .venv/bin/python -B -m pytest "
            "tests/test_wf2_replication.py tests/test_real_bridge.py "
            "tests/test_real_multimodel_batch.py tests/test_neural_health.py "
            "-q — 53 passed, 1 documented runpy warning in12.03s. Ruff check . "
            "PASS. Static exact command: .venv/bin/python "
            "scripts/check_python_types.py --pylance-dist "
            "/Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist "
            "—185 files,0 errors,0 warnings. Git diff --check PASS. Negative "
            "old/wrong approval refuses fitting. Telemetry one fabricated "
            "effective-batch update matches parameters/optimizer tensors/RNG "
            "bitwise. Actual read-only final-weight "
            "replay/matched-mask/conservation passes. Full legacy suite "
            "intentionally not run. Editor: select repository "
            ".venv/bin/python, installed Pylance basic/stubs; reload language "
            "server and refresh Problems, human confirmation still pending."
        ),
    ),
    (
        "11. Experiment/results summary",
        headline
        + "\n\n"
        + "\n\n".join(health_lines)
        + (
            "\n\nNo economic metrics or confirmation results. New pairs "
            "TA009-TM0-S42-WF2 and TA009-MC0-S42-WF2; seed42/December "
            "prefix/January–June2024. Exploratory candidate development "
            "results only."
        ),
    ),
    (
        "12. Reproduction instructions",
        (
            "Use README authoritative setup and documented locally entitled "
            "source/component inputs. Read commands.md and API doc. Fresh "
            "preparation regenerates numeric recipes but actual construction "
            "timestamps change recipe IDs. Fresh scientific fitting requires "
            "new exact approval and unconsumed IDs; consumed queue "
            "intentionally refuses retry. Read-only review uses explicit "
            "corrected plan/approval and safe CPU weights. No clean-clone "
            "rehearsal performed. Original WF1 entry points bind original code "
            "and fail closed against extended source; use original commit "
            "bbb8d223650dbc42a744fd910b76e30ffe3f04a8 and their original "
            "packets rather than weakening guards."
        ),
    ),
    (
        "13. Git / collaboration status",
        (
            f"Branch {pre['branch']}, HEAD {pre['HEAD']} unchanged; fetched at "
            f"startup, ahead1/behind0. No "
            f"staging/commit/push/pull/merge/stash/reset. All new "
            f"code/test/API/config/journal/reports remain uncommitted; three "
            f"execution files and registry pointer modified; external "
            f"RandomNotes edit retained. Protect local work before integration. "
            f"If separately authorized later, inspect inventory, stage approved "
            f"small source/tests/docs/config/metadata/session only, exclude "
            f"checkpoints and licensed sources, commit and use a reviewed PR; "
            f"no Git write was authorized in this task."
        ),
    ),
    (
        "14. Known issues, risks and limitations",
        (
            "No remaining failing focused tests or static errors. First "
            "launcher had __main__/canonical class identity mismatch and "
            "failed before STARTED; fixed, regression-tested and rebound with "
            "a new live approval. Second invocation used relative output, "
            "failed before STARTED/optimizer and collided with old summary; "
            "archived and corrected via absolute CLI output without changing "
            "approved source. No consumed-ID retry occurred. Historical "
            "preparation fitted-clock mismatch fixed using true construction "
            "time, with numeric recipes unchanged. "
        )
        + qual
        + (
            " One seed/five stocks and inspected development folds; paired "
            "intervals exploratory, no full G8/causal inference. Both-pass G6 "
            "warnings retained. Final editor refresh awaits human confirmation."
        ),
    ),
    (
        "15. Decisions requiring human or teammate review",
        (
            "Review WF2 results and warnings; no new approval needed for this "
            "completed scope. Any visualization app, changed "
            "target/loss/normalization, extra seed/fold/baseline, economic "
            "replay, finalist promotion, cap expansion or confirmation "
            "requires a separate scoped package/decision. Preserve ≤3-family "
            "finalist constraint; no current promotion."
        ),
    ),
    ("16. Next recommended steps", nexts),
    (
        "17. Artifact inventory",
        (
            f"{p}/artifact_inventory.csv includes each packet file, new "
            f"source/test/API/config/journal, modified bridge files and this "
            f"report with SHA/type/bytes/purpose; inventory excludes itself. "
            f"checkpoint files remain intentionally local/gitignored. Old "
            f"stores/weights/reports are linked and hash-protected; no "
            f"duplicate raw archive/dense windows/gradient tensors. "
            f"resource_and_elapsed.json distinguishes actual fit, worker, "
            f"supervisor, wrapper and package duration. "
        ),
    ),
]
with report.open("x") as f:
    f.write(
        "# Codex Session Report\n\n"
        + "\n\n".join("## " + head + "\n\n" + body for head, body in sections)
        + "\n"
    )
put(
    "report_metadata.json",
    {
        "session_report": str(report),
        "report_generation_seconds": time.monotonic() - began,
        "snapshot_at": now.isoformat(),
    },
)
print(
    json.dumps(
        {
            "report": str(report),
            "results": fit_table,
            "headline": headline,
            "preservation": list(changes),
            "package_elapsed": resource["package_elapsed_seconds_at_snapshot"],
        }
    )
)
