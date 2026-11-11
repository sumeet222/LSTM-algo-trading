"""Bounded independent witnesses for admitted inherited preprocessing."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import boundary
boundary.install()
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from geometry import STOCKS,SPLITS,QUARANTINE_NS,MINUTE,schedule,factor


def proxy_closes(frame: pd.DataFrame, op: int, close: int, previous: float) -> dict[int,float]:
    """Independent single-session cap5 witness, original unadjusted observations."""
    prices=dict(zip(frame["timestamp"].astype("int64"),frame["close"]))
    uncertain=set(); prev=previous
    for t,c in sorted(prices.items()):
        if np.isfinite(prev) and abs(np.log(c/prev))>np.log(1.25): uncertain.add((t-op)//(60*MINUTE))
        prev=c
    result={}; last=np.nan; trailing=0
    for k,start in enumerate(range(op,close,60*MINUTE)):
        end=min(start+60*MINUTE,close)
        timestamps=list(range(start,end,MINUTE)); vals=np.array([prices.get(t,np.nan) for t in timestamps])
        present=np.isfinite(vals); n=len(vals); j=0
        while j<n:
            if present[j]: last=vals[j]; trailing=0; j+=1; continue
            a=j
            while j<n and not present[j]: j+=1
            length=j-a+(trailing if a==0 else 0)
            if present.any() and k not in uncertain and length<=5 and np.isfinite(last):
                for t in timestamps[a:j]: result[t]=last
            trailing=length if j==n else 0
        if present[-1]: trailing=0
    return result


def run() -> None:
    sched=schedule(); bydate=sched.set_index("date"); manifest=[]; checks=[]; witness_counts={}; schemas={}
    split_days={(s,d) for s,d,_ in SPLITS}
    special={("COP","2012-04-30"),("COP","2012-05-01"),("AAPL","2024-11-29"),("AAPL","2024-03-08"),("AAPL","2024-03-11"),("VZ","2010-07-01")}
    for s,d,_ in SPLITS:
        ix=sched.index[sched["date"]==d][0]
        special.add((s,sched.iloc[ix-1]["date"])); special.add((s,d))
    totals={"hourly_rows":0,"canonical_rows":0,"canonical_rth":0,"quarantine_seen":0}
    observed_case=set()
    for month in boundary.MONTHS:
        frames={}
        for family in ("hourly","canonical"):
            path=boundary.data_path(family,month)
            pf=pq.ParquetFile(path)
            manifest.append({"family":family,"month":month,"path":str(path.relative_to(boundary.ROOT)),"bytes":path.stat().st_size,"sha256":boundary.sha256(path),"rows":pf.metadata.num_rows})
            schemas.setdefault(family,str(pf.schema_arrow))
            frames[family]=pf.read().to_pandas()
        h=frames["hourly"]; c=frames["canonical"]
        totals["hourly_rows"]+=len(h); totals["canonical_rows"]+=len(c)
        assert set(c.ticker)<=set(STOCKS) and set(h.ticker)==set(STOCKS)
        assert c.is_genuine.all() and not c.is_imputed.any()
        assert c.source_revision.eq("776328445b7ac6e7815ef3a483e9c8ded1eb6d56").all()
        assert h.source_revision.eq("776328445b7ac6e7815ef3a483e9c8ded1eb6d56").all()
        assert not c.duplicated(["ticker","timestamp"]).any()
        dates=pd.Series(c.timestamp.dt.tz_convert("America/New_York").dt.tz_localize(None).to_numpy(dtype="datetime64[D]").astype(str),index=c.index)
        ns=c.timestamp.astype("int64").to_numpy()
        # Independent membership, including DST and half-days, for every admitted canonical row.
        op=dates.map(bydate.open).astype("int64").to_numpy(); cl=dates.map(bydate.close).astype("int64").to_numpy()
        membership=(ns>=op)&(ns<cl)
        assert np.array_equal(membership,c.is_rth.to_numpy()),f"RTH calendar mismatch {month}"
        c=c.loc[membership].copy(); c["date"]=dates.loc[membership].to_numpy(); totals["canonical_rth"]+=len(c)
        for stock in STOCKS:
            sub=h.loc[h.ticker==stock]
            np.testing.assert_array_equal(sub.price_factor.to_numpy(),factor(stock,sub.session_date_et.to_numpy()))
            assert sub.volume_factor.eq(1).all()
        pick=set()
        for idx,row in h.iterrows():
            key=(row.ticker,row.session_date_et)
            qkeys=[(row.ticker,t) for t in range(row.hour_start_utc.value,row.hour_end_utc.value,MINUTE) if (row.ticker,t) in QUARANTINE_NS]
            if key in special or qkeys: pick.add(key)
            conditions={"proxy_terminal":np.isfinite(row.close_input_cap5) and not np.isfinite(row.close),
                        "missing_open":not np.isfinite(row.open) and row.genuine_count>0,
                        "missing_close_unfilled":not np.isfinite(row.close_input_cap5) and row.genuine_count>0,
                        "empty_hour":row.genuine_count==0,
                        "partial_volume":row.genuine_count>0 and row.missing_count>0,
                        "quarantine":row.quarantine_count>0}
            for name,yes in conditions.items():
                if yes and name not in observed_case: pick.add(key); observed_case.add(name)
        for stock,d in sorted(pick):
            df=c.loc[(c.ticker==stock)&(c.date==d)].sort_values("timestamp")
            prior=c.loc[(c.ticker==stock)&(c.timestamp<bydate.loc[d,"open"])]
            prev=float(prior.iloc[-1].close) if len(prior) else np.nan
            proxies=proxy_closes(df,bydate.loc[d,"open"].value,bydate.loc[d,"close"].value,prev)
            for _,row in h.loc[(h.ticker==stock)&(h.session_date_et==d)].iterrows():
                a=row.hour_start_utc.value; b=row.hour_end_utc.value
                r=df.loc[(df.timestamp>=row.hour_start_utc)&(df.timestamp<row.hour_end_utc)].copy()
                q=np.array([(stock,t.value) in QUARANTINE_NS for t in r.timestamp],dtype=bool)
                nq=int(q.sum()); totals["quarantine_seen"]+=nq
                r=r.loc[~q]; fac=float(factor(stock,[d])[0])
                vals={"genuine_count":len(r),"quarantine_count":nq,
                    "open":float(r.iloc[0].open)*fac if len(r) and r.iloc[0].timestamp.value==a else np.nan,
                    "close":float(r.iloc[-1].close)*fac if len(r) and r.iloc[-1].timestamp.value==b-MINUTE else np.nan,
                    "high":float(r.high.max())*fac if len(r) and not nq else np.nan,
                    "low":float(r.low.min())*fac if len(r) and not nq else np.nan,
                    "volume":float(r.volume.sum()) if len(r) else np.nan}
                vals["close_input_cap5"]=vals["close"] if np.isfinite(vals["close"]) else (proxies.get(b-MINUTE,np.nan)*fac if not nq else np.nan)
                for field,expected in vals.items():
                    actual=float(row[field]); ok=bool(np.isclose(expected,actual,rtol=1e-12,atol=1e-12,equal_nan=True))
                    checks.append({"specimen":f"{stock}/{d}/{row.hour_start_utc}","field":field,"expected":expected,"actual":actual,"pass":ok})
        print(month,"contract witnesses",len(checks),flush=True)
    failures=[x for x in checks if not x["pass"]]
    result={"status":"PASS" if not failures else "FAIL","totals":totals,"specimens":len({x["specimen"] for x in checks}),"checks":len(checks),"cases":sorted(observed_case),"failures":failures,"schemas":schemas}
    (boundary.PHASE/"audit/input_manifest.json").write_text(json.dumps(manifest,indent=2))
    (boundary.PHASE/"audit/aggregation_witnesses.json").write_text(json.dumps(checks,indent=2,allow_nan=True))
    (boundary.PHASE/"audit/data_contract_receipt.json").write_text(json.dumps(result,indent=2))
    text=f'''# Inherited data contract\n\nStatus: {result['status']}. Independent MODELING-LAYER replication with audited INHERITED preprocessing. Whole-history hourly aggregation, source validity/deduplication, source gap/conflict classification and cap5 construction remain inherited. This is not raw-to-results independence.\n\nThe 174 literal months in each admitted family (348 files) are bound by input_manifest.json (paths, bytes, SHA256, row counts). No broader market path inventory was made. Revision is 776328445b7ac6e7815ef3a483e9c8ded1eb6d56. Canonical rows are unadjusted genuine non-imputed observations; is_rth is independently checked against literal XNYS rules. Canonical extended hours are excluded. All canonical keys are unique. The fixed 18 quarantine records are removed and fixed nine splits independently applied only to price endpoints/witnesses; volume is unchanged. COP has its specified separate price bases.\n\nHourly open/close/high/low are action-adjusted genuine fields; close_input_cap5 is an input-only field, not a genuine label price. genuine_count/quarantine_count/missing_count/conflict_count/invalid_minutes/longest_gap_minutes remain distinct. Volume features will require genuine_count>0, missing_count<=5, longest_gap_minutes<=5, and zero conflicts/quarantine/invalid minutes. Missing volume is unknown; observed sums with acceptable absence remain lower bounds. completed_at_utc is bin completion, not measured vendor delivery; issue is separately assumed end+2minutes. Stubs never enter histories.\n\nBounded canonical aggregation witnesses cover {result['specimens']} stock-hours / {len(checks)} field assertions, nine split ex-dates and preceding sessions, COP boundary, all18 quarantines, ordinary hours, DST and half-day, missing open/terminal/empty hours and cap5 proxies. Independent proxy witness uses completed-bin rules and same-session carry. All fields compare with atol/rtol1e-12, NaN equality. Failures: {len(failures)}. Full schemas and cases are in data_contract_receipt.json; exact expected/actual values are in aggregation_witnesses.json.\n\nThis audit verifies admitted computational interpretation, not vendor authenticity, historical arrival/vintage, source rights, issuer lineage or point-in-time universe. Retrospective actions/quarantines and fixed survivor sample are accepted historical limitations. The known nominal-origin/issue mismatch is preserved. No historical FT16, labels, role indices, models, scores, calibrators or project helper imports are admitted.\n'''
    (boundary.PHASE/"audit/INHERITED_DATA_CONTRACT.md").write_text(text)
    print(json.dumps({k:v for k,v in result.items() if k!="schemas"},indent=2))
    if failures: raise RuntimeError("Inherited contract witness failure; no features or fits authorized")

if __name__=="__main__": run()
