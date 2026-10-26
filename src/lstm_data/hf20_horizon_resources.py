"""S3 resource policy: explicit user amendments, separate from frozen science."""

from __future__ import annotations

import json
import resource
import sys
from pathlib import Path

from .hf20_ranking_authority import fixed_project_bytes


def capacity_check(rss: int, task: int, project: int, caps: dict[str, int]) -> dict[str, int]:
    excess = dict(
        RAM_bytes=max(0, rss - caps["RAM_bytes"]),
        task_artifact_bytes=max(0, task - caps["task_artifact_bytes"]),
        project_bytes=max(0, project - caps["project_bytes"]),
    )
    if any(excess.values()):
        raise ValueError("S3_RESOURCE_CAP_REQUIRED_ADDITIONAL_BYTES:" + json.dumps(excess))
    return excess


def resources(out: Path) -> dict:
    policy = out / "RESOURCE_AMENDMENT_AUTHORITY_v1.json"
    caps = dict(
        task_artifact_bytes=1_000_000_000, project_bytes=10_000_000_000, RAM_bytes=2_000_000_000
    )
    if policy.exists():
        authority = json.loads(policy.read_text())
        if (
            authority["kind"] != "ACTUAL_DIRECT_USER_REQUEST"
            or authority["resource_only"] is not True
            or authority["additional_experiments_authorized"] != 0
        ):
            raise ValueError("S3_RESOURCE_AUTHORITY_REQUIRED")
        expected = dict(
            task_artifact_bytes=2_500_000_000, project_bytes=15_000_000_000, RAM_bytes=2_000_000_000
        )
        if authority["new_caps"] != expected:
            raise ValueError("S3_EXACT_APPROVED_RESOURCE_CAPS_REQUIRED")
        caps = expected
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform != "darwin":
        rss *= 1024
    task = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    project = fixed_project_bytes(Path.cwd().resolve(), out.resolve()) + task + 16_000_000
    observed = dict(peak_rss_bytes=rss, task_bytes=task, project_logical_bytes=project)
    excess = capacity_check(rss, task, project, caps)
    return dict(**observed, caps=caps, additional_capacity_required_bytes=excess)
