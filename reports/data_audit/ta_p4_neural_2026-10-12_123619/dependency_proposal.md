# PyTorch dependency proposal

PyTorch is absent from the repository .venv and dependency specification. The frozen TM0 engine requires real torch forward/backward and checkpoint tests; NumPy and current dependencies cannot implement those contracts. Proposed smallest change: add an optional neural extra containing torch==2.10.0 to pyproject.toml, document pip install -e .[dev,neural], and install this pinned package into the existing .venv without changing Python or other dependency constraints. No torchvision, torchaudio or additional accelerator stack is needed. CPU will be the deterministic synthetic audit default; inspect MPS only after installation.

The [official PyPI release](https://pypi.org/project/torch/2.10.0/) supplies a standard CPython 3.14 macOS 14+ ARM64 wheel, approximately 79.5 MB, plus declared transitive dependencies. The current environment details are in preflight.json. This is an established compatible release, not a request to upgrade Python or recreate the environment.

Proposed install after approval: .venv/bin/python -m pip install torch==2.10.0. Preserve existing dependency pins/settings; verify import, actual CPU backward, device availability and pip dependency consistency. If the resolver requires incompatible changes, stop rather than silently alter the environment.

Authorization required by supplied P4 prompt section 0.4: do not silently add heavyweight packages; if PyTorch is absent, report a dependency/installation proposal. No implementation is claimed complete while this dependency is missing. Original data and 0/40 scientific pair usage remain unchanged.

## Approved execution

The user approved the pinned dependency and installation during this package. Installed torch2.10.0 into the existing .venv, declared the optional neural extra and refreshed editable package metadata without runtime dependency upgrades. CPU backward and pip check passed. See torch_environment.json and final API/setup instructions; dependency is no longer a HOLD. Scientific approvals remain separate.
