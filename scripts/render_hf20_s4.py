"""Existing Chromium only: offline S4 filter QA and one PNG for each actual saved run."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(out: Path, browser: str | None = None) -> None:
    candidate = browser or shutil.which("chromium") or shutil.which("google-chrome")
    if candidate is None:
        mac = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if mac.is_file():
            candidate = str(mac)
    if candidate is None:
        raise ValueError("Existing browser required; no install authorized")
    views = []
    for p in sorted(out.glob("HF20-S4A-*/oos_scores.parquet")):
        run_id = p.parent.name
        views.append(
            (run_id, str(2000 + int(run_id.split("-")[2][1:])) + "|" + run_id.split("-")[4])
        )
    if not views:
        raise ValueError("NO_SAVED_S4_VIEWS")
    page = (out / "plots/s4_a_rankings.html").resolve().as_uri()
    receipts = []
    with tempfile.TemporaryDirectory(prefix="s4_local_browser_") as profile:
        flags = [
            candidate,
            "--headless",
            "--disable-gpu",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-default-apps",
            "--disable-sync",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            "--hide-scrollbars",
            "--host-resolver-rules=MAP * ~NOTFOUND",
            "--window-size=1600,1100",
            "--user-data-dir=" + profile,
        ]
        for run_id, key in views:
            image = out / "plots" / f"{run_id}.png"
            result = subprocess.run(
                flags
                + [
                    "--virtual-time-budget=5000",
                    "--screenshot=" + str(image.resolve()),
                    page + "?view=" + key,
                ],
                capture_output=True,
                timeout=90,
                check=False,
            )
            if result.returncode or not image.exists() or image.stat().st_size < 10000:
                raise ValueError("S4_PNG_FAILED", run_id)
            receipts.append(dict(run_id=run_id, png=str(image), bytes=image.stat().st_size))
        result = subprocess.run(
            flags + ["--virtual-time-budget=30000", "--dump-dom", page + "?qa=1"],
            capture_output=True,
            timeout=180,
            check=False,
        )
        match = re.search(r'<pre id="qa-result">(.*?)</pre>', result.stdout.decode(), re.S)
        if result.returncode or match is None:
            raise ValueError("S4_BROWSER_QA_INCOMPLETE", result.returncode)
        qa = json.loads(html.unescape(match.group(1)))
        if qa["status"] != "PASS":
            raise ValueError("S4_BROWSER_QA_FAILED", qa)
    (out / "S4_BROWSER_QA.json").write_text(
        json.dumps(dict(status="PASS", views=receipts, interactive=qa), indent=2) + "\n"
    )
    print("S4_OFFLINE_BROWSER_QA_PASS", len(views), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--browser")
    args = p.parse_args()
    run(args.out, args.browser)
