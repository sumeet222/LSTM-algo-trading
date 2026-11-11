"""Inspect only admitted input schemas; no feature construction."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import boundary
boundary.install()
import json
import platform
import importlib.metadata
import pyarrow.parquet as pq

result = {}
for family in ("hourly", "canonical"):
    path = boundary.data_path(family, "2010-07")
    table = pq.read_table(path)
    result[family] = {"schema": str(table.schema), "rows": len(table),
                      "sample": table.slice(0, 2).to_pylist()}
result["environment"] = {"python": sys.version, "platform": platform.platform(),
    "machine": platform.machine(), "packages": {n: importlib.metadata.version(n) for n in
    ("numpy", "pandas", "pyarrow", "torch", "exchange_calendars")}}
print(json.dumps(result, indent=2, default=str))
(boundary.PHASE / "audit" / "initial_schema.json").write_text(json.dumps(result, indent=2, default=str))
