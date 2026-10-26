"""Render local Plotly HTML with an already installed Chromium; never installs a browser."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(out: Path, browser: str | None) -> None:
    candidate = browser or shutil.which("chromium") or shutil.which("google-chrome")
    if candidate is None:
        mac = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if mac.is_file():
            candidate = str(mac)
    if candidate is None:
        raise ValueError("Use --browser with an existing Chromium executable; no installation")
    receipt = {}
    with tempfile.TemporaryDirectory(prefix="hf20_local_plot_review_") as profile:
        flags = [
            candidate,
            "--headless",
            "--disable-gpu",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-sync",
            "--disable-default-apps",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--hide-scrollbars",
            "--host-resolver-rules=MAP * ~NOTFOUND",
            "--window-size=1600,1000",
            "--user-data-dir=" + profile,
        ]
        for year in range(2021, 2025):
            path = out / "plots" / f"historical_{year}.png"
            result = subprocess.run(
                flags
                + [
                    "--virtual-time-budget=5000",
                    "--screenshot=" + str(path.resolve()),
                    (out / "plots" / f"historical_{year}_static.html").resolve().as_uri(),
                ],
                capture_output=True,
                timeout=60,
                check=False,
            )
            if result.returncode or not path.exists() or path.stat().st_size < 10000:
                raise ValueError("LOCAL_PNG_RENDER_FAILED", year, result.returncode)
            receipt[str(year)] = dict(png=str(path), bytes=path.stat().st_size)
            print("Rendered", year, flush=True)
        result = subprocess.run(
            flags
            + [
                "--virtual-time-budget=20000",
                "--dump-dom",
                (out / "plots" / "historical_s1_s2_rankings.html").resolve().as_uri() + "?qa=1",
            ],
            capture_output=True,
            timeout=120,
            check=False,
        )
        dom = result.stdout.decode()
        match = re.search(r'<pre id="qa-result">(.*?)</pre>', dom, re.S)
        if result.returncode or match is None:
            raise ValueError("INTERACTIVE_QA_DID_NOT_COMPLETE", result.returncode)
        receipt["interactive"] = json.loads(html.unescape(match.group(1)))
        if receipt["interactive"]["status"] != "PASS":
            raise ValueError(receipt["interactive"])
    (out / "HISTORICAL_BROWSER_QA.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("LOCAL_OFFLINE_RENDER_AND_FILTER_QA_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--browser")
    args = parser.parse_args()
    run(args.out, args.browser)
