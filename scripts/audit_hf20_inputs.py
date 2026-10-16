"""Independent real HF20 training-only floor/volume checks; never fits a model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.config import write_json
from lstm_data.hf20_features import build_components
from lstm_data.hf20_loader import require_approval
from lstm_data.hf20_oracles import average
from lstm_data.hf20_source import SYMBOLS, read_source, verify_source


def audit(contract_path: Path, out: Path) -> None:
    contract = json.loads(contract_path.read_text())
    require_approval(
        Path.cwd(),
        contract["approval"],
        proposal_sha=contract["proposal_sha256"],
        amendment_ref=contract.get("amendment_approval"),
    )
    recipes = json.loads(Path(contract["recipes"]["path"]).read_text())
    frame = read_source(verify_source())
    c = build_components(
        frame,
        start="2022-06-01",
        stop="2026-01-06",
        independent_daily_close=contract["feature_id"].endswith("V2"),
    )
    rows = []
    for name, recipe in recipes.items():
        eligible = np.asarray(
            c.grid.session.between("2022-12-01", recipe["fit_stop_inclusive"]), dtype=bool
        )
        daily_mask = np.asarray(
            ["2022-12-01" <= day <= recipe["fit_stop_inclusive"] for day in c.regular_days],
            dtype=bool,
        )
        for j, symbol in enumerate(SYMBOLS):
            # Scalar rolling oracle over source O/C, independently of production components.
            oc = np.log(c.source["close"][:, j] / c.source["open"][:, j])
            h12 = np.asarray([average(oc[: i + 1], 12, 12, rms=True) for i in range(len(oc))])
            h60 = np.asarray([average(oc[: i + 1], 60, 57, rms=True) for i in range(len(oc))])
            h = np.concatenate([h12[eligible], h60[eligible]])
            h = h[np.isfinite(h) & (h > 0)]
            price = c.daily_close[:, j]
            changes = np.diff(np.log(price), prepend=np.nan)
            d = np.asarray([average(changes[: i + 1], 63, 60, rms=True) for i in range(len(price))])
            d = d[daily_mask]
            d = d[np.isfinite(d) & (d > 0)]
            hv = c.source["volume"][eligible, j]
            hv = hv[np.isfinite(hv) & (hv > 0)]
            dv = c.daily_volume[daily_mask, j]
            dv = dv[np.isfinite(dv) & (dv > 0)]
            expected = dict(
                hourly_floor=float(np.percentile(h, 5)),
                daily_floor=float(np.percentile(d, 5)),
                hourly_pseudocount=0.01 * float(np.median(hv)),
                daily_pseudocount=0.01 * float(np.median(dv)),
            )
            actual = recipe["floors"][j]
            for parameter, value in expected.items():
                passed = bool(np.isclose(value, actual[parameter], rtol=1e-10, atol=1e-12))
                if not passed:
                    raise ValueError("HF20_INDEPENDENT_FLOOR_OR_VOLUME_MISMATCH")
                rows.append(
                    dict(
                        recipe=name,
                        symbol=symbol,
                        parameter=parameter,
                        independent=value,
                        stored=actual[parameter],
                        passed=passed,
                    )
                )
    out.mkdir(parents=True, exist_ok=False)
    pd.DataFrame(rows).to_csv(out / "floor_and_volume_arithmetic_oracles.csv", index=False)
    write_json(
        out / "floor_and_volume_checks.json",
        dict(
            passed=all(r["passed"] for r in rows),
            equations=len(rows),
            source="Actual permitted pre-held-out source",
            neural_fits=0,
            ridge_fits=0,
        ),
    )
    print(json.dumps(dict(equations=len(rows), passed=True, training=False)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    audit(args.contract, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
