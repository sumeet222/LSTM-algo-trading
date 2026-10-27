"""Add requested saved-trajectory risk plots to the existing offline S5/S9 renderer.

This is presentation only. It loads no raw source, fits no parameters and leaves
all sealed training/diagnostic source and per-run PASS bundles unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import resource
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from lstm_data import hf20_s5s9_visual as visual
from lstm_data.hf20_s5s9 import RUNS
from lstm_data.hf20_s5s9_run import resources

JS = Path(__file__).with_suffix(".js").read_text()


def render_complete(out: Path, *, reuse_screenshots: bool = False) -> None:
    """Decorate generated HTML, retaining all original and additional browser gates."""
    base = visual.dashboard

    def decorated(folder: Path, *, rehearsal: bool = False) -> Path:
        if rehearsal:
            raise ValueError("THIS_EXTENSION_IS_FOR_COMPLETED_SAVED_RUNS_ONLY")
        path = base(folder, rehearsal=False)
        content = path.read_text()
        original = folder / "S5_S9_VISUAL_DIAGNOSTICS_GENERATED_BASE.html"
        if not original.exists():
            original.write_text(content)
        needle = "'Source age diagnostic; not appended S5 metadata');}"
        assert content.count(needle) == 1
        content = content.replace(needle, needle[:-1] + "await supplementary(v,rows);}")
        anchor = "$('run').onchange=refreshTicker;"
        assert content.count(anchor) == 1
        content = content.replace(anchor, JS + "\n" + anchor)
        content = content.replace(
            "<h2>Actual start inventory</h2>",
            "<p>Additional plots below use the visible saved ticker/date trajectory. "
            "Rolling windows contain up to20 visible observations and are retrospective "
            "diagnostics, not input features or full-role weighted performance. "
            "Full-role metrics and conditional strata use every saved row.</p>"
            '<div class="grid"><div class="plot" id="diagnostic_scatter"></div>'
            '<div class="plot" id="diagnostic_error"></div>'
            '<div class="plot" id="diagnostic_rolling"></div></div>'
            "<h2>Actual start inventory</h2>",
        )
        content = content.replace(
            "'quality','movement']",
            "'quality','movement','diagnostic_scatter','diagnostic_error','diagnostic_rolling']",
        )
        path.write_text(content)
        (folder / "S5_S9_SUPPLEMENTARY_VIEW.js").write_text(JS)
        return path

    path = out / "S5_S9_VISUAL_DIAGNOSTICS.html"
    old_loop = "for(let run of runs){$('run').value=run;"
    new_loop = (
        "for(let run of (query.has('qa_run')?[query.get('qa_run')]:runs)){$('run').value=run;"
    )
    old_call = "if(query.has('qa'))qa();"
    new_call = (
        "if(query.has('qa'))qa().finally(()=>{"
        "for(const tag of document.querySelectorAll('script'))tag.textContent='';});"
    )
    if not reuse_screenshots:
        decorated(out)
    else:
        snapshot = out / "S5_S9_VISUAL_DIAGNOSTICS_FAILED_FULL_BATCH.html"
        if not snapshot.exists():
            resources(out, path.stat().st_size)
            shutil.copyfile(path, snapshot)
    content = path.read_text()
    before_sha = hashlib.sha256(content.encode()).hexdigest()
    if old_loop in content:
        patched = content.replace(old_loop, new_loop).replace(old_call, new_call)
        assert patched.replace(new_loop, old_loop).replace(new_call, old_call) == content
        path.write_text(patched)
    else:
        assert new_loop in content and new_call in content
    del content
    browser = (
        shutil.which("chromium")
        or shutil.which("google-chrome")
        or ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    )
    assert Path(browser).is_file()
    plots = out / "plots"
    plots.mkdir(exist_ok=True)
    receipts, cases = [], []
    resources(out, 20_000_000)
    with tempfile.TemporaryDirectory(prefix="s5s9_chunked_browser_") as profile:
        flags = [
            browser,
            "--headless",
            "--disable-gpu",
            "--disable-background-networking",
            "--disable-extensions",
            "--no-first-run",
            "--hide-scrollbars",
            "--host-resolver-rules=MAP * ~NOTFOUND",
            "--window-size=1600,1100",
            "--user-data-dir=" + profile,
        ]
        for run in RUNS:
            png = plots / (run + ".png")
            if not reuse_screenshots:
                subprocess.run(
                    flags
                    + [
                        "--virtual-time-budget=4000",
                        "--screenshot=" + str(png.resolve()),
                        path.resolve().as_uri() + "?view=" + run,
                    ],
                    capture_output=True,
                    timeout=90,
                    check=True,
                )
            assert png.exists() and png.stat().st_size > 10000
            result = subprocess.run(
                flags
                + [
                    "--virtual-time-budget=30000",
                    "--dump-dom",
                    path.resolve().as_uri() + "?qa=1&qa_run=" + run,
                ],
                capture_output=True,
                timeout=180,
                check=True,
            )
            match = re.search(r'<pre id="qa-result">(.*?)</pre>', result.stdout.decode(), re.S)
            assert match is not None, run
            qa = json.loads(html.unescape(match.group(1)))
            assert qa["status"] == "PASS" and len(qa["cases"]) == 4, qa
            assert {c["role"] for c in qa["cases"]} == {
                "oos",
                "inner_train",
                "inner_validation",
                "refit",
            }
            for case in qa["cases"]:
                assert case["run"] == run and case["status"] == "PASS"
                source = out / run / (case["role"] + "_metrics.json")
                assert case["rows"] == json.loads(source.read_text())["rows"]
            cases.extend(qa["cases"])
            receipts.append(dict(run=run, png=str(png), bytes=png.stat().st_size))
            print("S5S9_VIEW_PASS", run, "4 roles,13 plot panels", flush=True)
    assert len(cases) == 64 and len(receipts) == 16
    ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
        1 if sys.platform == "darwin" else 1024
    )
    assert ram <= 2_000_000_000
    report = dict(
        status="PASS",
        rehearsal=False,
        views=receipts,
        interactive=dict(status="PASS", cases=cases),
        qa_batches=16,
        plot_panels_per_case=13,
        reused_screenshots=reuse_screenshots,
        screenshot_source_before_qa_only_patch_sha256=before_sha,
        html_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        peak_rss_bytes=ram,
    )
    (out / "BROWSER_QA.json").write_text(json.dumps(report, indent=2) + "\n")
    numerical = json.loads((out / "S5_S9_NUMERICAL_VERIFICATION.json").read_text())
    numerical.update(
        status="PASS_COMPLETE",
        browser_status="PASS",
        browser_views=16,
        browser_role_cases=64,
        browser_plot_panels_per_case=13,
        final_resources=resources(out),
    )
    (out / "S5_S9_VERIFICATION.json").write_text(json.dumps(numerical, indent=2) + "\n")
    print("S5S9_BROWSER_PASS 16 64", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--reuse-screenshots", action="store_true")
    args = parser.parse_args()
    render_complete(args.out, reuse_screenshots=args.reuse_screenshots)
