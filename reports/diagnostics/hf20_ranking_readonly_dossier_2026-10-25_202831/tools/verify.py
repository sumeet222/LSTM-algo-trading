"""Independent fixed-outcome operand/source-witness and preservation verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from audit import BASE, ROLES, Reader, digest, table


def verify(out: Path) -> None:
    reader = Reader(out)
    contract = json.loads(Path(reader.manifest["source_contract"]["path"]).read_text())
    recipes = json.loads(Path(contract["fit_recipes"]["path"]).read_text())
    clock = reader.table(Path(contract["files"]["origins"]["path"]), "refit")
    reports, thresholds = [], []
    for role in ROLES:
        phase = "inner" if role.startswith("inner") else "refit"
        f = reader.table(BASE / "A7_immediate_diagnostics" / role / "T2_S42.parquet", role)
        order = {t: i for i, t in enumerate(contract["symbols"])}
        f["j"] = f.ticker.map(order)
        f = f.sort_values(["origin_id", "j"])
        r = f.return_4h.to_numpy(float).reshape(-1, 20)
        median = np.median(r, axis=1)
        mad = np.median(abs(r - median[:, None]), axis=1)
        np.testing.assert_allclose(
            f.cross_section_median, np.repeat(median, 20), rtol=1e-11, atol=1e-12
        )
        np.testing.assert_allclose(f.cross_section_mad, np.repeat(mad, 20), rtol=1e-11, atol=1e-12)
        np.testing.assert_allclose(
            f.numerator, (r - median[:, None]).reshape(-1), rtol=1e-11, atol=1e-12
        )
        admitted = clock.loc[clock[role + "_admitted"]]
        assert set(admitted.origin_id) == set(f.origin_id)
        assert (admitted.entry_index - admitted.first_step).eq(47).all()
        assert (admitted.exit_index - admitted.entry_index).eq(4).all()
        start = pd.to_datetime(admitted.entry_end_utc, utc=True)
        end = pd.to_datetime(admitted.exit_end_utc, utc=True)
        issued = pd.to_datetime(admitted.issuance_utc, utc=True)
        mature = pd.to_datetime(admitted.label_maturity_utc, utc=True)
        assert (end - start).eq(pd.Timedelta(hours=4)).all()
        assert (issued - start).eq(pd.Timedelta(minutes=2)).all()
        assert (mature - end).eq(pd.Timedelta(minutes=2)).all()
        assert mature.lt(pd.Timestamp("2026-01-01", tz="UTC")).all()
        reports.append(
            dict(
                role=role,
                first_session=str(admitted.session_date_et.min()),
                last_session=str(admitted.session_date_et.max()),
                origin_count=len(admitted),
                session_count=admitted.session_date_et.nunique(),
                earliest_origin=str(start.min()),
                latest_maturity=str(mature.max()),
                target_operands="PASS 20-return median/MAD/numerator",
                clock="PASS exact scheduled geometry",
            )
        )
        if role in ("inner_train", "refit"):
            thresholds.append(
                dict(
                    phase=phase,
                    epsilon=recipes[phase]["epsilon"],
                    scale=recipes[phase]["t2_scale"],
                    train_frozen_event_p95=float(np.quantile(abs(f.TG20), 0.95)),
                    train_frozen_event_p99=float(np.quantile(abs(f.TG20), 0.99)),
                    frozen_recipe_path=contract["fit_recipes"]["path"],
                    frozen_recipe_sha256=contract["fit_recipes"]["sha256"],
                )
            )
    table(out, "role_chronology_and_operand_checks.csv", reports)
    table(out, "phase_thresholds.csv", thresholds)
    croot = BASE / "A7_immediate_diagnostics/refit"
    cases = reader.table(croot / "cases.parquet", "refit")
    candles = reader.table(croot / "case_candles.parquet", "refit")
    returns = reader.table(croot / "case_20_returns.parquet", "refit")
    rows = []
    for row in cases.to_dict("records"):
        cid = row["case_id"]
        c = candles.loc[candles.case_id.eq(cid)].sort_values("step")
        operands = returns.loc[returns.case_id.eq(cid)]
        assert len(c) == 52 and len(operands) == 20
        hist = c.iloc[:48]
        a, b = c.iloc[47], c.iloc[-1]
        assert bool(a.genuine_close) and bool(b.genuine_close)
        actual = float(np.log(float(b.close) / float(a.close)))
        ref = operands.set_index("ticker").loc[[row["ticker"]], "return_4h"].iloc[0]
        np.testing.assert_allclose(actual, float(ref), rtol=1e-11, atol=1e-12)
        r = operands.return_4h.to_numpy(float)
        med = float(np.median(r))
        mad = float(np.median(abs(r - med)))
        target = (actual - med) / (mad + float(row["epsilon"]))
        np.testing.assert_allclose(target, row["TG20"], rtol=1e-11, atol=1e-12)
        rows.append(
            dict(
                case_id=cid,
                case_role=row["case_role"],
                origin_id=row["origin_id"],
                ticker=row["ticker"],
                selection=row["selection"],
                input_steps=48,
                label_future_steps=4,
                target_reconstruction_error=target - row["TG20"],
                input_proxy_count=int(hist.proxy_count.sum()),
                input_assumed_missing_volume=int(hist.assumed_zero_missing_count.sum()),
                actual_TG20=row["TG20"],
                numerator=actual - med,
                mad=mad,
                epsilon=row["epsilon"],
                source_candles_path=str(croot / "case_candles.parquet"),
                source_case_id=cid,
            )
        )
    table(out, "preserved_source_witness_checks.csv", rows)
    # A7/A12 cases are the same events, not independent replication.
    acases = reader.table(BASE / "A12_immediate_diagnostics/refit/cases.parquet", "refit")
    assert cases[["origin_id", "ticker", "case_role"]].equals(
        acases[["origin_id", "ticker", "case_role"]]
    )
    current = []
    for r in reader.manifest["evidence"]:
        actual = digest(Path(r["path"]))
        assert actual == r["sha256"]
        current.append(dict(path=r["path"], before=r["sha256"], after=actual, unchanged=True))
    table(out, "source_preservation.csv", current)
    journal = Path("reports/audit/track_a_real_pairs_v18_p028.jsonl")
    events = [json.loads(line) for line in journal.read_text().splitlines()]
    assert events[-1]["global_started_pairs"] == 62
    (out / "verification_receipt.json").write_text(
        json.dumps(
            dict(
                status="PASS",
                preserved_inputs=len(current),
                protected_files_byte_only=len(reader.manifest["protected"]),
                source_cases=len(rows),
                source_cases_distinct_not66=True,
                ledger_before=62,
                ledger_after=62,
                journal_sha256=digest(journal),
                code_sha256=digest(Path(__file__)),
                no_optimizer_steps=True,
                no_model_forwards=True,
                no_new_horizon_labels=True,
            ),
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    verify(p.parse_args().out)
