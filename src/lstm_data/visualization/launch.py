"""One local launcher with bounded port selection and read-only setup diagnostics."""

from __future__ import annotations

import argparse
import errno
import importlib.util
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from .loaders import Catalog, ViewUnavailable


def available_port(preferred: int) -> int:
    if not 1024 <= preferred <= 65515:
        raise ValueError("Choose a port between1024 and65515.")
    for port in range(preferred, preferred + 20):
        with socket.socket() as server:
            try:
                server.bind(("127.0.0.1", port))
            except OSError as exc:
                if exc.errno == errno.EADDRINUSE:
                    continue
                raise
            return port
    raise ValueError("No free local port in the next20 ports. Choose --port <number>.")


def streamlit_command(port: int) -> list[str]:
    return [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "apps/track_a_dashboard.py",
        "--server.address",
        "127.0.0.1",
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
        "--server.fileWatcherType",
        "none",
    ]


def server_smoke(root: Path, port: int) -> int:
    """Start this app only, GET localhost health/HTML, then SIGINT this child and measure it."""
    started = time.monotonic()
    command = streamlit_command(port)
    proc = subprocess.Popen(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result: dict = {"url": f"http://127.0.0.1:{port}", "command": command}
    try:
        while time.monotonic() - started < 30:
            try:
                with urllib.request.urlopen(result["url"] + "/_stcore/health", timeout=0.5) as r:
                    result["health_status"] = r.status
                    result["health_body"] = r.read().decode()
                result["startup_to_health_seconds"] = time.monotonic() - started
                break
            except (urllib.error.URLError, TimeoutError):
                if proc.poll() is not None:
                    raise RuntimeError("Local server exited before health readiness")
                time.sleep(0.1)
        else:
            raise TimeoutError("Local server health was not ready within30 seconds")
        t = time.monotonic()
        with urllib.request.urlopen(result["url"], timeout=5) as r:
            result["html_status"], result["html_bytes"] = r.status, len(r.read())
        result["html_request_seconds"] = time.monotonic() - t
    finally:
        t = time.monotonic()
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
        output, _ = proc.communicate(timeout=10)
        result["SIGINT_shutdown_seconds"] = time.monotonic() - t
        result["server_return_code"] = proc.returncode
        result["server_log"] = output.decode(errors="replace")
        print(json.dumps(result, indent=2))
    return 0 if proc.returncode == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("TRACK_A_DASHBOARD_PORT", "8501"))
    )
    parser.add_argument(
        "--check", action="store_true", help="Validate local setup without a server"
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Measure local health/HTML and clean SIGINT shutdown; then exit",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    if importlib.util.find_spec("torch") is None:
        print(
            "The existing research environment is missing its declared neural extra. "
            "Follow README setup before adding visualization. No package is installed here."
        )
        return 2
    missing = [name for name in ("streamlit", "plotly") if importlib.util.find_spec(name) is None]
    if missing:
        print("Missing free visualization packages in the repository .venv: " + ", ".join(missing))
        print('From the repository root: .venv/bin/python -m pip install -e ".[visualization]"')
        return 2
    try:
        catalog = Catalog.discover(root)
        if args.check:
            refs = catalog.token()
            missing_files = catalog.missing_required(refs)
            if missing_files:
                print(f"PARTIAL: {len(missing_files)} required local artifacts are missing:")
                for name in missing_files[:10]:
                    print("  " + name)
                print(
                    "Provision the exact artifacts using data/README.md and their manifests. "
                    "Optional checkpoint weights are not required for saved-score displays."
                )
                return 2
            print(
                f"PASS local setup: {len(refs)} bound file/stat dependencies; "
                "WF1 TM0/MC0/MC1/E5, WF2 TM0/MC0; no fitting or source download."
            )
            return 0
        port = available_port(args.port)
    except (OSError, ValueError, ViewUnavailable) as exc:
        print(f"Local setup unavailable: {exc}")
        return 2
    if port != args.port:
        print(f"Port{args.port} is occupied; using free local port{port}.", flush=True)
    print(f"Open http://localhost:{port} in your browser", flush=True)
    print("Localhost only · read-only research · stop with Ctrl+C", flush=True)
    if args.smoke:
        return server_smoke(root, port)
    os.chdir(root)
    os.execv(sys.executable, streamlit_command(port))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
