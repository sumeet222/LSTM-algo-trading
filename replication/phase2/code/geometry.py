"""Independent schedule, fixed retrospective actions, and source geometry."""
from __future__ import annotations
from datetime import date, timedelta
import numpy as np
import pandas as pd

STOCKS = ("VZ", "COP", "BAC", "BA", "AAPL", "PEP", "MRK", "SBUX", "CVX", "MS", "AMD", "KO", "JNJ", "AMZN", "XOM", "WFC", "AVGO", "TSLA", "MA", "CSCO")
SPLITS = (("KO","2012-08-13",2),("MA","2014-01-22",10),("AAPL","2014-06-09",7),("SBUX","2015-04-09",2),("AAPL","2020-08-31",4),("TSLA","2020-08-31",5),("AMZN","2022-06-06",20),("TSLA","2022-08-25",3),("AVGO","2024-07-15",10))
QUARANTINE = (("AAPL","2010-08-31 18:39"),("AAPL","2010-08-31 18:43"),("AAPL","2010-09-07 16:00"),("AAPL","2010-09-07 16:39"),("TSLA","2010-11-19 20:39"),("TSLA","2010-11-19 20:55"),("AAPL","2010-12-17 20:55"),("AMZN","2010-12-08 16:26"),("AMZN","2010-12-08 16:42"),("BAC","2011-01-25 15:10"),("AAPL","2011-01-03 18:43"),("AAPL","2011-01-13 16:31"),("AAPL","2011-02-18 20:32"),("AAPL","2011-02-18 20:40"),("AMZN","2011-03-25 17:02"),("AMZN","2011-03-25 17:14"),("AMZN","2011-06-23 17:53"),("BAC","2011-10-10 13:37"))
QUARANTINE_NS = {(s, pd.Timestamp(t, tz="UTC").value) for s,t in QUARANTINE}
MINUTE = 60_000_000_000


def _easter(y: int) -> date:
    a,b,c = y%19,y//100,y%100
    d,e = b//4,b%4
    f=(b+8)//25; g=(b-f+1)//3
    h=(19*a+b-d-g+15)%30
    i,k=c//4,c%4
    l=(32+2*e+2*i-h-k)%7
    m=(a+11*h+22*l)//451
    return date(y,(h+l-7*m+114)//31,(h+l-7*m+114)%31+1)


def _nth(y: int,m: int,weekday: int,n: int) -> date:
    first=date(y,m,1)
    return first+timedelta(days=(weekday-first.weekday())%7+7*(n-1))


def _observed(d: date) -> date:
    return d+timedelta(days=1 if d.weekday()==6 else -1 if d.weekday()==5 else 0)


def schedule() -> pd.DataFrame:
    """Literal §3 rules; no exchange-calendar implementation used here."""
    holidays=set()
    for y in range(2010,2026):
        new=date(y,1,1)
        holidays.update((new+timedelta(days=1) if new.weekday()==6 else new,
            _nth(y,1,0,3),_nth(y,2,0,3),_easter(y)-timedelta(days=2),
            date(y,5,31)-timedelta(days=date(y,5,31).weekday()),
            _observed(date(y,7,4)),_nth(y,9,0,1),_nth(y,11,3,4),_observed(date(y,12,25))))
        if y>=2022: holidays.add(_observed(date(y,6,19)))
    holidays.update(date.fromisoformat(s) for s in ("2012-10-29","2012-10-30","2018-12-05","2025-01-09"))
    rows=[]
    for stamp in pd.date_range("2010-07-01","2025-01-10",freq="D"):
        d=stamp.date()
        if d.weekday()>4 or d in holidays: continue
        half=(d==_nth(d.year,11,3,4)+timedelta(days=1) or
              (d.month==12 and d.day==24 and d.weekday()<4) or
              (d.month==7 and d.day==3 and (d.weekday() in (0,1,3) or d.year>=2013 and d.weekday()==2)) or
              (d.year<2013 and d.month==7 and d.day==5 and d.weekday()==4))
        op=pd.Timestamp(f"{d} 09:30",tz="America/New_York").tz_convert("UTC")
        cl=pd.Timestamp(f"{d} {'13:00' if half else '16:00'}",tz="America/New_York").tz_convert("UTC")
        rows.append((str(d),op,cl,half))
    result=pd.DataFrame(rows,columns=["date","open","close","early_close"])
    for field in ("open","close"):
        result[field]=result[field].dt.as_unit("ns")
    return result


def endpoint(t: int, session: int, sched: pd.DataFrame, minutes: int=240) -> tuple[int,int]:
    cursor=t; remaining=minutes*MINUTE
    for j in range(session,len(sched)):
        op=int(sched.iloc[j]["open"].value); close=int(sched.iloc[j]["close"].value)
        if close<=cursor: continue
        cursor=max(cursor,op)
        available=close-cursor
        if remaining<=available: return cursor+remaining,j
        remaining-=available; cursor=close
    raise ValueError("Calendar exhausted")


def grids(sched: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
    hours=[]; origins=[]
    for d in range(len(sched)):
        row=sched.iloc[d]
        if row["date"]>"2024-12-31": continue
        opening=row["open"]; closing=row["close"]
        if not isinstance(opening,pd.Timestamp) or not isinstance(closing,pd.Timestamp):
            raise TypeError("Schedule open and close must be timestamps")
        op=int(opening.value); cl=int(closing.value)
        n=(cl-op)//(60*MINUTE)
        for k in range(n): hours.append((d,row["date"],op+k*60*MINUTE,op+(k+1)*60*MINUTE,k))
        for k in range(n+1):
            t=op+k*60*MINUTE
            if t>=cl: continue
            e,es=endpoint(t,int(d),sched)
            clock=np.zeros(10,dtype=np.float32); clock[k]=1
            clock[7]=(cl-t)/MINUTE/240; clock[8]=int(e>cl)
            clock[9]=(date.fromisoformat(str(sched.iloc[d+1]["date"]))-date.fromisoformat(str(row["date"]))).days/7
            origins.append((d,row["date"],t,e,e+2*MINUTE,es,k,6 if k==0 else k-1,"OVERNIGHT" if e>cl else "INTRADAY",row["early_close"],clock))
    h=pd.DataFrame(hours,columns=["session","date","start","end","slot"])
    o=pd.DataFrame(origins,columns=["session","date","t","e","maturity","exit_session","slot_index","context","category","early_close","clock"])
    ends=h["end"].to_numpy()
    o["entry_index"]=np.searchsorted(ends,o["t"].to_numpy(),side="right")-1
    o["first_step"]=o["entry_index"]-47
    return h,o


def factor(stock: str, dates):
    result=np.ones(len(dates),dtype=np.float64)
    for s,d,r in SPLITS:
        if s==stock: result[np.asarray(dates)<d]/=r
    return result


def volume_regime(stock: str, dates):
    result=np.zeros(len(dates),dtype=np.int16)
    for s,d,_ in SPLITS:
        if s==stock: result+=np.asarray(dates)>=d
    return result


def price_basis(stock: str, dates):
    return (np.asarray(dates)>="2012-05-01").astype(np.int8) if stock=="COP" else np.zeros(len(dates),dtype=np.int8)
