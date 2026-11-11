"""ISOLATED OFFLINE prefix preparation. Never imported by runtime producer.

Only this boundary accepts matured historical outcome observations. No neural fitting.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import hashlib
import json
import math
from statistics import median
from .contracts import utc
from .risk_sizing import RiskReference


@dataclass(frozen=True)
class RiskRecipe:
    version: str = 'TRACK2_PREFIX_MEDIAN_V1'
    minimum_count: int = 40
    absolute_floor: float = 1e-6
    floor_fraction: float = .25
    units: str = 'absolute_log_return'


@dataclass(frozen=True)
class MaturedPrefixObservation:
    ticker: str
    slot: str
    origin: datetime
    endpoint: datetime
    available_at: datetime
    magnitude: float
    basis: str
    source_hash: str
    late_corrected: bool = False


def prepare(rows: tuple[MaturedPrefixObservation,...],fold: str,ticker: str,slot: str,
            fit_start: datetime,cutoff: datetime,basis: str,source_inventory_hash: str,
            recipe: RiskRecipe=RiskRecipe()) -> dict:
    if not source_inventory_hash or recipe.units!='absolute_log_return' or recipe.minimum_count<40 or recipe.absolute_floor<=0 or recipe.floor_fraction<=0:
        raise ValueError('INVALID_RISK_RECIPE_OR_LINEAGE')
    accepted=[];excluded=0
    for r in rows:
        # Check cutoff BEFORE accessing magnitude, flags, or unit from later data.
        if utc(r.origin)<utc(fit_start) or utc(r.endpoint)>=utc(cutoff) or utc(r.available_at)>=utc(cutoff):
            excluded+=1;continue
        if r.ticker!=ticker or r.slot!=slot:
            continue
        if (r.origin>=r.endpoint or r.available_at<r.endpoint or r.basis!=basis or r.late_corrected or not r.source_hash
                or not math.isfinite(r.magnitude) or r.magnitude<0):
            raise ValueError('INVALID_PREFIX_OBSERVATION')
        accepted.append(r)
    keys=[r.origin for r in accepted]
    if len(set(keys))!=len(keys):
        raise ValueError('DUPLICATE_PREFIX_ORIGIN')
    b=float(median(r.magnitude for r in accepted)) if accepted else 0.
    status='READY' if len(accepted)>=recipe.minimum_count and b>0 else 'RISK_REFERENCE_INSUFFICIENT_PREFIX_SUPPORT'
    return {'fold':fold,'ticker':ticker,'slot':slot,'fit_start':utc(fit_start).isoformat(),
            'cutoff':utc(cutoff).isoformat(),'basis':basis,'units':recipe.units,'recipe':asdict(recipe),
            'source_inventory_hash':source_inventory_hash,'count':len(accepted),'excluded_boundary_count':excluded,
            'latest_available_at':max((utc(r.available_at).isoformat() for r in accepted),default=None),
            'sample_origin_min':min((utc(r.origin).isoformat() for r in accepted),default=None),
            'sample_origin_max':max((utc(r.origin).isoformat() for r in accepted),default=None),
            'status':status,'b':b if status=='READY' else None,
            'm_floor':max(recipe.absolute_floor,recipe.floor_fraction*b) if status=='READY' else None}


def write_manifest(path: Path,records: list[dict],source_inventory: list[dict]) -> str:
    if path.exists():
        raise ValueError('APPEND_ONLY_REFERENCE_REQUIRED')
    payload={'recipe':'TRACK2_PREFIX_MEDIAN_V1','source_inventory':source_inventory,'records':records}
    checksum=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    path.write_text(json.dumps({'payload':payload,'sha256':checksum},indent=2)+'\n')
    return checksum


def load_reference(path: Path,fold: str,ticker: str,slot: str,basis: str,
                   expected_checksum: str,expected_inventory_hash: str) -> RiskReference:
    obj=json.loads(path.read_text());payload=obj['payload']
    actual=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if actual!=obj['sha256'] or actual!=expected_checksum:
        raise ValueError('RISK_MANIFEST_IDENTITY_MISMATCH')
    rows=[r for r in payload['records'] if (r['fold'],r['ticker'],r['slot'])==(fold,ticker,slot)]
    if len(rows)!=1:
        raise ValueError('RISK_REFERENCE_MISSING_OR_AMBIGUOUS')
    r=rows[0]
    if (r['basis']!=basis or r['source_inventory_hash']!=expected_inventory_hash or r['units']!='absolute_log_return'
            or r['status']!='READY' or r['count']<40 or not 0<r['b'] or not 0<r['m_floor']):
        raise ValueError('RISK_REFERENCE_PROVENANCE_OR_SUPPORT_MISMATCH')
    return RiskReference(ticker,fold,slot,float(r['b']),float(r['m_floor']),datetime.fromisoformat(r['latest_available_at']),datetime.fromisoformat(r['cutoff']),actual)
