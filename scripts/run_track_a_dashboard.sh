#!/usr/bin/env bash
set -eu
VIZ_ROOT="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$VIZ_ROOT"
if [ ! -x .venv/bin/python ]; then
  echo 'Repository .venv is missing. Follow README setup, then install .[visualization].' >&2
  exit 2
fi
exec .venv/bin/python -m lstm_data.visualization.launch "$@"
