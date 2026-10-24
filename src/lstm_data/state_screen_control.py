"""Read-only same-slot ten-session historical-state replacement; no neural fitting."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import write_json
from .controlled_loss import LossPolicy
from .hf1m_ft16_source import ref
from .state_screen_data import cache_key, donor_map, panel_from_rows, pool_for
from .state_screen_engine import state_hash
from .state_screen_metrics import allocation, metrics, paired
from .state_screen_models import StateModel


def evaluate(
    model: StateModel,
    study,
    view,
    population: pd.DataFrame,
    training: pd.DataFrame,
    recipe: dict,
    destination: Path,
    *,
    rehearsal: bool = False,
) -> dict:
    """Score original and shifted predictions on the same complete20 diagnostic subset."""
    model.eval()
    before = state_hash(model)
    pool = study.origins.copy() if rehearsal else pool_for(study, view)
    mapping = donor_map(view.source.rows, pool)
    mapping.to_parquet(destination / "peer_shift_mapping.parquet", index=False)
    selected = mapping.loc[mapping.status.eq("MATCHED")].reset_index(drop=True)
    summary: dict[str, object] = dict(
        status="PASS_P028_MATCHED_PEER_INFORMATION_CONTROL",
        role=view.split,
        lag_eligible_sessions=10,
        available_origins=len(mapping),
        matched_origins=len(selected),
        matched_stock_rows=len(selected) * 20,
        excluded_by_reason=mapping.loc[~mapping.status.eq("MATCHED")]
        .status.value_counts()
        .to_dict(),
        cache_key=cache_key(view, mapping),
        donor_label_values_read=False,
        own_history_unchanged=True,
        scope="Diagnostic distribution shift; not a trained null, causal identification or p-value",
        source_rule=(
            "source_input_eligible only, same-slot exact10 prior eligible ses"
            "sions; no label or future-availability selection"
        ),
    )
    if len(selected):
        representation = []
        predictions = []
        references = []
        policy = LossPolicy("T2", scale=recipe["scale"])
        with torch.inference_mode():
            for start in range(0, len(selected), 16):
                batch = selected.iloc[start : start + 16]
                positions = tuple(int(v) for v in batch.position)
                own = view.origin_batch(positions)["x"]
                donor = panel_from_rows(view, pool.iloc[batch.donor_position.to_numpy(dtype=int)])
                own_tensor = torch.from_numpy(own)
                neutral = model.shifted(own_tensor, own_tensor)
                shifted = model.shifted(own_tensor, torch.from_numpy(donor))
                from .state_screen_models import panel_state

                original_details = model.details(own_tensor)
                shifted_details = model.details(own_tensor, panel_state(torch.from_numpy(donor)))
                for key in ("readout", "alpha", "router", "global_hidden", "global_cell"):
                    if key in original_details:
                        delta = shifted_details[key] - original_details[key]
                        representation.append(
                            dict(batch=start, module=key, rms=float(delta.square().mean().sqrt()))
                        )
                references.append(
                    torch.stack((neutral, policy.canonical(neutral)), -1).reshape(-1, 2).numpy()
                )
                predictions.append(
                    torch.stack((shifted, policy.canonical(shifted)), -1).reshape(-1, 2).numpy()
                )
        scores = np.concatenate(predictions)
        neutral_scores = np.concatenate(references)
        original = (
            population.set_index(["origin_id", "ticker"])
            .reindex(
                pd.MultiIndex.from_product(
                    [selected.origin_id, population.ticker.drop_duplicates()],
                    names=["origin_id", "ticker"],
                )
            )
            .reset_index()
        )
        if len(original) != len(selected) * 20 or original.TG20.isna().any():
            raise ValueError("P028_EXACT_MATCHED_CONTROL_ROWS")
        native = original.pred_original_TG20.to_numpy().copy()
        np.testing.assert_allclose(neutral_scores[:, 1].astype(float), native, rtol=7e-7, atol=1e-7)
        original["native_original_prediction"] = native
        original["raw_net_output"] = neutral_scores[:, 0]
        original["pred_original_TG20"] = neutral_scores[:, 1].astype(float)
        summary["neutral_vs_native_max_absolute_error"] = float(
            abs(neutral_scores[:, 1].astype(float) - native).max()
        )
        summary["reference_scoring"] = (
            "Original and shifted use identical focal-counterfactual batching; "
            "neutral model.shifted(own,own) matches canonical saved outputs within "
            "unchanged inverse tolerance7e-7/1e-7. Main checkpoint full-population "
            "reload tolerance remains exactly0."
        )
        original = allocation(original, recipe["scale"])
        changed = original.copy()
        changed["raw_net_output"] = scores[:, 0]
        changed["pred_original_TG20"] = scores[:, 1].astype(float)
        changed = allocation(changed, recipe["scale"])
        original.to_parquet(destination / "peer_original_matched.parquet", index=False)
        changed.to_parquet(destination / "peer_shifted_matched.parquet", index=False)
        summary["representation_changes"] = representation
        summary["original"] = metrics(original, training)
        summary["shifted"] = metrics(changed, training)
        summary["output_rms_change"] = float(
            np.sqrt(np.mean((changed.pred_original_TG20 - original.pred_original_TG20) ** 2))
        )
        summary["output_mean_change"] = float(
            (changed.pred_original_TG20 - original.pred_original_TG20).mean()
        )
        movement = []
        for dimension in ("ticker", "era", "month", "V1_state", "quality", "fallback_state"):
            if dimension not in original:
                continue
            for value, indices in original.groupby(dimension, dropna=False).indices.items():
                a = original.iloc[indices]
                b = changed.iloc[indices]
                w = a.ordinary_weight.to_numpy()
                w = w / w.sum()
                delta = b.pred_original_TG20.to_numpy() - a.pred_original_TG20.to_numpy()
                y = a.TG20.to_numpy()
                movement.append(
                    dict(
                        dimension=dimension,
                        value=str(value),
                        rows=len(a),
                        origins=a.origin_id.nunique(),
                        sessions=a.session_date_et.nunique(),
                        original_MSE=float(w @ ((a.pred_original_TG20.to_numpy() - y) ** 2)),
                        shifted_MSE=float(w @ ((b.pred_original_TG20.to_numpy() - y) ** 2)),
                        mean_output_change=float(w @ delta),
                        RMS_output_change=float(np.sqrt(w @ (delta**2))),
                        positive_change_fraction=float(w @ (delta > 0)),
                        semantics=(
                            "Matched conditional weighted moments; "
                            "not within-origin IC for partial-stock groups"
                        ),
                    )
                )
        pd.DataFrame(movement).to_parquet(destination / "peer_shift_slices.parquet", index=False)
        comparisons, daily = paired(changed, original)
        comparisons["interpretation"] = (
            "shifted minus original on identical matched subset; distribution"
            "-shifting diagnostic, not a neural null"
        )
        write_json(destination / "peer_shift_paired.json", comparisons)
        daily.to_parquet(destination / "peer_shift_daily.parquet", index=False)
    else:
        summary["status"] = "EMPTY_P028_CAUSAL_DONOR_SUBSET"
        summary["original"] = None
        summary["shifted"] = None
        population.iloc[:0].to_parquet(destination / "peer_original_matched.parquet", index=False)
        population.iloc[:0].to_parquet(destination / "peer_shifted_matched.parquet", index=False)
        pd.DataFrame(
            columns=[
                "dimension",
                "value",
                "rows",
                "origins",
                "sessions",
                "original_MSE",
                "shifted_MSE",
                "mean_output_change",
                "RMS_output_change",
                "positive_change_fraction",
                "semantics",
            ]
        ).to_parquet(destination / "peer_shift_slices.parquet", index=False)
    if state_hash(model) != before:
        raise ValueError("P028_PEER_CONTROL_CHANGED_MODEL")
    summary["model_state_unchanged"] = True
    summary["mapping"] = ref(destination / "peer_shift_mapping.parquet")
    write_json(destination / "peer_information_control.json", summary)
    return summary
