"""Preserve legacy numerical bindings while registering the additive P021 entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lstm_data.config import atomic_new, digest
from lstm_data.hf1m_ft16_source import ref
from lstm_data.real_batch_authority import atomic_replace_json


def update(out: Path) -> None:
    path = Path("configs/track_a_visualization_v1.json")
    snapshot = out / "visualization_config_before_p021.json"
    if not snapshot.exists():
        atomic_new(snapshot, path.read_bytes())
    original = json.loads(snapshot.read_text())
    c = json.loads(path.read_text())
    app = "apps/track_a_dashboard.py"
    c["readers"][app] = digest(Path(app))
    for r in c["controlled_explorer"]["cache_readers"]:
        if r["path"] == app:
            r["sha256"] = digest(Path(app))
    c["hf1m_long_additive_compatibility"] = dict(
        previous_config=ref(snapshot),
        study_config="configs/track_a_hf1m_long_visualization_v1.json",
        change="Additive HF1M route only; legacy numerical/result/scaler references unchanged",
    )
    for key, value in original.items():
        if key not in ("readers", "controlled_explorer") and c[key] != value:
            raise ValueError("P021_LEGACY_EVIDENCE_CHANGED:" + key)
    old_readers = dict(original["readers"])
    old_readers[app] = c["readers"][app]
    if old_readers != c["readers"]:
        raise ValueError("P021_UNRELATED_READER_CHANGE")
    old_controlled = json.loads(json.dumps(original["controlled_explorer"]))
    for r in old_controlled["cache_readers"]:
        if r["path"] == app:
            r["sha256"] = digest(Path(app))
    if old_controlled != c["controlled_explorer"]:
        raise ValueError("P021_LEGACY_CONTROLLED_CHANGE")
    atomic_replace_json(path, c)
    print("PASS additive reader binding; all legacy numerical evidence unchanged")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    update(p.parse_args().out)
