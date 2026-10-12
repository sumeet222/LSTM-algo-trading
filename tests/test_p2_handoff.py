"""Deferred scientific constraints must survive the portable P3/P4 handoff."""

import json
from pathlib import Path

import pytest

from lstm_data.config import digest
from lstm_data.p2_closure import HANDOFF_CONFIG, load_deferred_work


def test_real_versioned_register_retains_all_seed_ids_and_scientific_holds():
    entries = load_deferred_work(HANDOFF_CONFIG)
    assert len(entries) == 16
    assert {f"P2-DEF-{i:03d}" for i in range(1, 15)} <= {e["id"] for e in entries}
    assert all(e["scientific_status"] == "HOLD" for e in entries)
    assert all(
        not e["blocks_engineering"] for e in entries if e["responsible_phase"].startswith("P2")
    )
    assert entries[13]["status"] == entries[15]["status"] == "RESOLVED_ENGINEERING_ONLY"
    assert json.loads(HANDOFF_CONFIG.read_text())["empirical_work_authorized"] is False


@pytest.mark.parametrize("mutation", ["delete", "boolean", "doc", "permission"])
def test_handoff_rejects_lost_dependency_changed_evidence_or_empirical_permission(
    tmp_path, mutation
):
    binding = json.loads(HANDOFF_CONFIG.read_text())
    register = json.loads(Path(binding["register"]["path"]).read_text())
    doc = Path(binding["readable_register"]["path"]).read_text()
    config_path = tmp_path / "configs" / "handoff.json"
    config_path.parent.mkdir()
    json_path, doc_path = tmp_path / "register.json", tmp_path / "register.md"
    if mutation == "delete":
        register["entries"] = register["entries"][1:]
    elif mutation == "boolean":
        register["entries"][0]["blocks_scientific_activation"] = "false"
    elif mutation == "permission":
        binding["empirical_work_authorized"] = True
    json_path.write_text(json.dumps(register))
    doc_path.write_text(doc)
    binding["register"] = {"path": "register.json", "sha256": digest(json_path)}
    binding["readable_register"] = {"path": "register.md", "sha256": digest(doc_path)}
    if mutation == "doc":
        doc_path.write_text(doc + "\nUnreviewed alteration\n")
    config_path.write_text(json.dumps(binding))
    with pytest.raises(ValueError, match="P2_|REGISTER"):
        load_deferred_work(config_path)
