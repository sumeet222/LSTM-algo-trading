# Rapid V2 reuse and runtime plan

V1's verified final registry, 15 MB feature cache, raw-share minute reader,
XNYS geometry, strategy evaluator, action processor, V5 next-valid-bar
execution and V1 physical/virtual account are the inputs. The V1 code,
cache, menus, results and older research objects are checked read-only.
The funding and inventory paths must be replayed for changed horizons or
commitments. One 48-month price traversal feeds all 108 accounts, including
18 baseline parity accounts. Each strategy's pretrade signal runs once per
frame and is shared across its six independent account books.

The allocation adapter multiplies V1's eligible budget by 1.00, .85 or .70
before equal allocation, paired leg weights, name caps and share rounding.
All downstream hard caps, own cash, borrow, stale marks, reserve, expiry,
physical order slots and pair logic retain V1 rules. Open and pending
commitments are never retrospectively resized.

Retail session horizons use the same nominal Eastern slot on the Nth
subsequent XNYS session. If that session lacks the slot, the candidate
abstains before an order exists. Scheduled-minute variants preserve the
V1 endpoint convention at the exact session close. Only calendar geometry
extends beyond 2024. Receipt and execution retain V1 time guards.

Keep one month of raw market data in memory, V1 feature arrays, compact
accounts, daily NAV, grouped counters and deterministic year-end state.
A shared vector screen finds possible cap breaches. The inherited exact
book still decides each prospective order and reconciles every fill.
The engine records aggregate reasons and costs with bounded examples.
Expected incremental peak RSS below 2 GB, disk below 100 MB and wall time
under 30 minutes, subject to a measured January pilot projection. The hard
output ceiling is 200 MB. Checkpoint publications bind code, source,
configuration, frontier, accounts and outcome digests. A resume skips
committed sessions and reads the unprocessed suffix of the original tape.
No raw market duplicate, signal regeneration, or order-level journal export.
