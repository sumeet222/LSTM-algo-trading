"""Update additive dashboard reader hashes while preserving the prior viewer config."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lstm_data.config import atomic_new, digest
from lstm_data.hf20_training_authority import reference
from lstm_data.real_batch_authority import atomic_replace_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    path = Path("configs/track_a_visualization_v1.json")
    snapshot = args.out / "visualization_config_before_hf20.json"
    if not snapshot.exists():
        atomic_new(snapshot, path.read_bytes())
    c = json.loads(path.read_text())
    app = "apps/track_a_dashboard.py"
    c["readers"][app] = digest(Path(app))
    for ref in c["controlled_explorer"]["cache_readers"]:
        if ref["path"] == app:
            ref["sha256"] = digest(Path(app))
    for name in ("hf20.py", "hf20_ui.py"):
        p = Path("src/lstm_data/visualization") / name
        c["readers"][str(p)] = digest(p)
    c["hf20_additive_compatibility"] = dict(
        previous_config=reference(snapshot),
        study_config="configs/track_a_hf20_visualization_v1.json",
        change=(
            "Additive HF20 route/readers only; "
            "all five-stock result/data/recipe references preserved"
        ),
    )
    atomic_replace_json(path, c)
    old = json.loads(snapshot.read_text())
    for key, value in old.items():
        if key not in ("readers", "controlled_explorer") and c[key] != value:
            raise ValueError("LEGACY_VIEW_EVIDENCE_CHANGED:" + key)
    assert (
        c["controlled_explorer"]["cache_readers"][1:]
        == old["controlled_explorer"]["cache_readers"][1:]
    )
    print("HF20 additive reader bindings updated; legacy evidence references unchanged")


if __name__ == "__main__":
    main()
