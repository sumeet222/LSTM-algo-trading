"""Real HF20 finite batches and bitwise normalized-tensor oracle, without a model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from lstm_data.config import digest, write_json
from lstm_data.hf20_features import BOUNDED, COMMON, ORDER
from lstm_data.hf20_loader import load_hf20_train_data


def check(contract_path: Path, out: Path) -> None:
    contract = json.loads(contract_path.read_text())
    recipes = json.loads(Path(contract["recipes"]["path"]).read_text())
    results = {}
    for split, recipe in (
        ("inner_train", "inner"),
        ("inner_validation", "inner"),
        ("refit", "refit"),
        ("development", "refit"),
    ):
        view = load_hf20_train_data(contract_path, split=split, recipe=recipe)
        batch = view.batch((0, len(view.rows) // 2, len(view.rows) - 1))
        results[split] = dict(
            origins=len(view.rows),
            sessions=view.rows.session.nunique(),
            sample_shape=list(batch.x.shape),
            finite=bool(np.isfinite(batch.x).all()),
            all_labels_valid=bool(batch.label_valid.all()),
            x_sha256=hashlib.sha256(batch.x.tobytes()).hexdigest(),
            sample_sessions=batch.sessions,
            recipe_id=batch.recipe_id,
        )
        if not results[split]["finite"]:
            raise ValueError("HF20_REAL_BATCH_NOT_FINITE")
    view = load_hf20_train_data(contract_path, split="development", recipe="refit")
    positions = (0, len(view.rows) // 2, len(view.rows) - 1)
    batch = view.batch(positions)
    with np.load(contract["store"]["path"], allow_pickle=False) as store:
        native = store["native_refit"]
        m2 = store["native_m2_refit"]
        day_index = store["day_index"]
    expected = np.empty_like(batch.x)
    for sample, position in enumerate(positions):
        row = view.rows.iloc[position]
        last = int(row.last_step)
        origin = int(row.origin) - 1
        history = np.arange(last - 47, last + 1)
        for k, feature in enumerate(ORDER):
            value = (
                m2[day_index[history], :, origin].T
                if feature == "M2"
                else native[history, :, COMMON.index(feature)].T
            )
            if feature not in BOUNDED:
                p = recipes["refit"]["scalers"][feature]
                value = (
                    np.zeros_like(value)
                    if p["method"] == "CONSTANT_ZERO"
                    else (value - p["center"]) / p["scale"]
                )
            expected[sample, ..., k] = value.astype(np.float32)
    if not np.array_equal(expected, batch.x):
        raise ValueError("HF20_NORMALIZED_FLOAT32_TENSOR_ORACLE")
    for split in ("held_out", "confirmation", "legacy_five_stock"):
        try:
            load_hf20_train_data(contract_path, split=split)
        except ValueError:
            continue
        raise ValueError("HF20_PROTECTED_OR_LEGACY_SPLIT_NOT_DENIED")
    write_json(
        out,
        dict(
            contract_sha256=digest(contract_path),
            preparation_id=contract["preparation_id"],
            stages=results,
            bitwise_float32_normalization_equal=True,
            independent_development_tensor_cells=int(expected.size),
            protected_and_legacy_splits_denied=True,
            neural_fits=0,
            ridge_fits=0,
            held_out_numeric_rows=0,
        ),
    )
    print(
        json.dumps(
            dict(
                stages=list(results),
                float32_oracle_cells=int(expected.size),
                passed=True,
                training=False,
            )
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    check(args.contract, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
