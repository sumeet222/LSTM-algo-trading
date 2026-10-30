"""Single-use uniform strict999 GARCH successor; all old scores remain frozen."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

from . import hf20_classical as old
from . import hf20_matched as parent
from .hf20_matched_math import apply_common, fit_common

b, c3 = old.b, old.c3
OUT = Path("reports/experiments/hf20_s9_mag_garch_strict999_2026-10-29")
NEURAL = {"CLOCK": old.clock.OUT / "s2b_clock", "S2C": old.S2C, "S5C": old.HYBRID}
BASES = tuple(NEURAL) + old.ARMS


def journal(status: str, **details: object) -> None:
    """Append-only task journal, separate from frozen neural ledger."""
    with (OUT / "research_journal.jsonl").open("a") as stream:
        stream.write(
            json.dumps(
                dict(
                    status=status,
                    at=pd.Timestamp.now(tz="UTC").isoformat(),
                    neural_ledger=186,
                    **details,
                ),
                allow_nan=False,
            )
            + "\n"
        )


def preservation() -> int:
    """Only explicit permitted predecessors; never scan protected sources."""
    bindings = b.read(OUT / "predecessor_bindings.json")
    for name, sha in bindings.items():
        assert b.digest(Path(name)) == sha, ("CHANGED_PREDECESSOR", name)
    return len(bindings)


def resources() -> dict:
    project = int(subprocess.check_output(["du", "-sk", "."], text=True).split()[0]) * 1024
    task = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    assert project < b.CAPS["project_bytes"] and task < b.CAPS["task_bytes"]
    return dict(project_bytes=project, task_bytes=task, peak_rss_bytes=b.memory())


def load_panel(year: int, role: str) -> pd.DataFrame:
    """Read frozen predecessor scores; no old calibration or neural inference."""
    return pd.read_parquet(parent.OUT / f"F{year % 100}/{role}_scores.parquet")


def panel_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(
        pd.util.hash_pandas_object(frame[[*c3.META, "A"]], index=False).to_numpy().tobytes()
    ).hexdigest()


def calibrate() -> None:
    """Exactly one common calibration per frozen source/fold; no rerun path."""
    preservation()
    guard = OUT / "calibration_started.json"
    b.write(guard, dict(at=pd.Timestamp.now(tz="UTC").isoformat()), new=True)
    tick = time.monotonic()
    complete_garch = b.read(OUT / "garch_status.json")["status"] == "COMPLETE"
    assert complete_garch
    bases = ["GARCH11-STRICT999"]
    records, checks, parity, inventory, supports = [], [], [], [], []
    for year in b.YEARS:
        cal, oos = load_panel(year, "calibration"), load_panel(year, "oos")
        if complete_garch:
            for role, f in [("calibration", cal), ("oos", oos)]:
                source = pd.read_parquet(OUT / f"GARCH/F{year % 100}/{role}_scores.parquet")
                pd.testing.assert_frame_equal(
                    f[[*c3.META, "A"]], source[[*c3.META, "A"]], check_dtype=False
                )
                f["GARCH11-STRICT999-UNCAL"] = source["GARCH11-STRICT999-UNCAL"]
        dest = OUT / f"F{year % 100}"
        dest.mkdir()
        for category in ["GLOBAL", *c3.GROUPS]:
            h = cal if category == "GLOBAL" else cal.loc[cal.category.eq(category)]
            mass = h.groupby("session_date_et").weight.sum().to_numpy()
            p = mass / mass.sum()
            supports.append(
                dict(
                    year=year,
                    group=category,
                    rows=len(h),
                    origins=h.origin_id.nunique(),
                    sessions=len(mass),
                    category_mass=float(mass.sum()),
                    normalized_session_weight_max=float(p.max()),
                    session_hhi=float(p @ p),
                    n_eff=float(1 / (p @ p)),
                    kappa=25,
                )
            )
        for name in bases:
            raw = name + "-UNCAL"
            coefs = fit_common(cal, raw)
            for c in coefs:
                records.append(dict(year=year, model=name, **c))
            for family in ["G", "IO"]:
                arm = f"MATCH-{name}-{family}"
                cal[arm] = apply_common(cal, raw, coefs, family)
                oos[arm] = apply_common(oos, raw, coefs, family)
                before = pd.DataFrame(oos[raw].to_numpy().reshape(-1, 20)).rank(axis=1)
                after = pd.DataFrame(oos[arm].to_numpy().reshape(-1, 20)).rank(axis=1)
                changed = int(np.any(before.to_numpy() != after.to_numpy(), axis=1).sum())
                zero = any(c["k"] == 0 for c in coefs if c["family"] == family)
                if not zero:
                    np.testing.assert_array_equal(before, after)
                parity.append(
                    dict(
                        year=year,
                        model=name,
                        family=family,
                        changed_rank_origins=changed,
                        zero_scalar=zero,
                        zero_raw_rows=int(oos[raw].eq(0).sum()),
                    )
                )
                if family == "G" and name in old.ARMS:
                    np.testing.assert_allclose(oos[arm], oos[name + "-CAL"], rtol=1e-13, atol=1e-15)
                inventory.append(
                    dict(
                        year=year,
                        arm=arm,
                        status="COMPLETE",
                        input=raw,
                        calibration_family=family,
                        rows=len(oos),
                        key_label_weight_sha256=panel_hash(oos),
                    )
                )
            journal("CALIBRATED", year=year, model=name, global_k=coefs[0]["k"])
        for role, f in [("calibration", cal), ("oos", oos)]:
            checks.append(dict(year=year, role=role, rows=len(f), sha256=panel_hash(f)))
            f.to_parquet(dest / f"{role}_scores.parquet", index=False, compression="zstd")
        resources()
    pd.DataFrame(supports).to_csv(OUT / "calibration_support.csv", index=False)
    pd.DataFrame(records).to_csv(OUT / "calibration_coefficients.csv", index=False)
    pd.DataFrame(parity).to_csv(OUT / "rank_parity.csv", index=False)
    pd.DataFrame(inventory).to_csv(OUT / "model_inventory.csv", index=False)
    b.write(
        OUT / "calibration_receipt.json",
        dict(
            status="COMPLETE",
            bases=bases,
            checks=checks,
            calibrator_families=2,
            model_fold_family_count=len(bases) * 8,
            old_calibrators_refitted=0,
            neural_inference=0,
            seconds=time.monotonic() - tick,
            **resources(),
        ),
    )
    journal("CALIBRATION_COMPLETE", models=len(bases), seconds=time.monotonic() - tick)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["garch", "calibrate", "report", "verify"])
    parser.add_argument("--output", type=Path, help="New output directory for report-only replay")
    args = parser.parse_args()
    if args.output is not None and args.action != "report":
        parser.error("--output is report-only")
    if args.action == "garch":
        from .hf20_strict999_fit import run

        run()
    elif args.action == "calibrate":
        try:
            calibrate()
        except Exception:
            (OUT / "calibration_failure.txt").write_text(traceback.format_exc())
            b.write(OUT / "calibration_blocked.json", dict(status="BLOCKED_CALIBRATION"), new=True)
            journal("BLOCKED_CALIBRATION")
            raise
    elif args.action == "report":
        from .hf20_strict999_report import report

        report(args.output)
    else:
        from .hf20_strict999_report import verify

        verify()


if __name__ == "__main__":
    main()
