"""Small self-contained Plotly viewer for authentic saved ranking diagnostics."""

from __future__ import annotations

import json
from pathlib import Path


def page(payload: dict, plotly_js: str) -> str:
    data = json.dumps(payload, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
    template = Path(__file__).with_name("hf20_rank_visual_template.html").read_text()
    return template.replace("__PLOTLY__", plotly_js).replace("__DATA__", data)
