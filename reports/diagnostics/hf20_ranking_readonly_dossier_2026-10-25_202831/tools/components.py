"""Exact cohort attribution retaining the cross-term that cancels only in full panels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from audit import BASE, ROLES, Reader, ranked, table, weights


def parts(y: np.ndarray, p: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    e = (y - p).reshape(-1, 20)
    common = np.repeat(e.mean(1), 20)
    centered = e.reshape(-1) - common
    values = common**2, centered**2, 2 * common * centered
    np.testing.assert_allclose(sum(values), (y - p) ** 2, rtol=1e-13, atol=1e-13)
    return values


def audit(out: Path) -> None:
    reader = Reader(out)
    contract = json.loads(Path(reader.manifest["source_contract"]["path"]).read_text())
    order = {s: i for i, s in enumerate(contract["symbols"])}
    rows = []
    for role in ROLES:
        b = reader.table(BASE / "A7_immediate_diagnostics" / role / "T2_S42.parquet", role)
        b["stock_order"] = b.ticker.map(order)
        b = b.sort_values(["origin_id", "stock_order"]).reset_index(drop=True)
        w = weights(b)
        y = b.TG20.to_numpy(float)
        baseline = parts(y, b.pred_original_TG20.to_numpy(float))
        masks = {"ALL": np.ones(len(b), bool)}
        for pct in (1, 5):
            m = ranked(abs(y), b, pct)
            masks[f"TARGET_TOP{pct}"] = m
            masks[f"TARGET_TOP{pct}_COMPLEMENT"] = ~m
        for arm in ("A7", "A12"):
            f = reader.table(
                BASE / f"{arm}_immediate_diagnostics" / role / "population.parquet", role
            )
            f["stock_order"] = f.ticker.map(order)
            f = f.sort_values(["origin_id", "stock_order"]).reset_index(drop=True)
            np.testing.assert_array_equal(f.TG20, b.TG20)
            candidate = parts(y, f.pred_original_TG20.to_numpy(float))
            for label, mask in masks.items():
                delta = [float(w[mask] @ (a[mask] - c[mask])) for a, c in zip(candidate, baseline)]
                full = float(
                    w[mask]
                    @ (
                        (y[mask] - f.pred_original_TG20.to_numpy()[mask]) ** 2
                        - (y[mask] - b.pred_original_TG20.to_numpy()[mask]) ** 2
                    )
                )
                np.testing.assert_allclose(sum(delta), full, rtol=1e-11, atol=1e-13)
                rows.append(
                    dict(
                        role=role,
                        arm=arm,
                        cohort=label,
                        weight_mass=float(w[mask].sum()),
                        delta_common=delta[0],
                        delta_centered=delta[1],
                        delta_cross_term=delta[2],
                        delta_mse=full,
                    )
                )
    table(out, "component_by_target_cohort.csv", rows)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    audit(p.parse_args().out)
