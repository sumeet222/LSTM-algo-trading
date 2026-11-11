import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import boundary
boundary.install()
import pyarrow.parquet as pq
import numpy as np
from geometry import schedule
t=time.monotonic(); s=schedule(); print("schedule",time.monotonic()-t,flush=True)
t=time.monotonic(); c=pq.read_table(boundary.data_path("canonical","2010-07")).to_pandas(); print("read",time.monotonic()-t,flush=True)
t=time.monotonic(); d=c.timestamp.dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d"); print("dates",time.monotonic()-t,flush=True)
t=time.monotonic(); op=d.map(s.set_index("date").open).astype("int64").to_numpy(); print("map",time.monotonic()-t,flush=True)
t=time.monotonic(); ns=c.timestamp.astype("int64").to_numpy(); print("int",time.monotonic()-t,flush=True)
