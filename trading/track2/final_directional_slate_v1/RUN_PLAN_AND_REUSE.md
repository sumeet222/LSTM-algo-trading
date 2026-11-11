# Runtime and reuse plan

First consolidate five verified archived books; no identical financial replay.
Existing compact daily, annual, grouped ticker/side and final captured cohort
records support comparison/ranking. M04 V2 individual top-five net tails are not
retained: report unavailable without reconstructing fictitious amounts. Registry
and score audit precede overlay outputs.

Read original magnitude partitions once (~1005 small files); recover input-only
magnitudes, ignore five-day sign/g columns. Recompute classical median/EWMA once
from mmap matured_source_moves and movement_geometry using strict prior receipt.
Share one compact NPZ cache (~5MB) and prior prefix references; no neural import.
The same-slot source windows are original scheduled60/min40/strict-missingness,
not a per-strategy recursive rebuild. Source validity is independent of outcomes.

At most12 MATCHED books, then <=9 non-EQUAL ATTAINABLE books; reuse unchanged
ATTAINABLE EQUAL archived accounts. These two bounded passes retain original
V2 fixed M04 versus V3 dynamic engine paths and use the same raw source loader,
not a V5 recorder. A single local market-day iterator feeds each engine group
per pass. Calendar, features, actions and risk arrays are shared. No data download.

Preflight estimate: risk input preparation<30s; pilot10 sessions<10s; full two
source passes about2–5minutes from prior146-second13-account benchmark. Peak RAM
~1.5–2GB, bounded reader concurrency1. Target financial/report<50MB, hard total200MB;
no per-minute logs. Per-account compact cohorts, physical fills, daily NAV and
reason/constraint aggregates; immutable annual restart checkpoints only if needed.
Source-backed pilot2024-11-18–2024-12-02 and synthetic witnesses precede full sizing.
If interrupted inspect process lock/run receipt/frontier first; never overwrite or
start a duplicate. Each population completes into its own immutable run directory;
completed populations are reused rather than rerun. State-level resume requires
full code/config/source/scenario binding and exactly-once proof, otherwise restart
only the incomplete population under a new ID and preserve aborted artifacts.
