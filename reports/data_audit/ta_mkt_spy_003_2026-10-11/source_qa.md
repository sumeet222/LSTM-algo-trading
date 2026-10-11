# TA-MKT-SPY-003 measured canonical source QA

**PASS: immutable archive, native grid, research warm-up and structural coverage.**
**HOLD: historical publication and complete action certification.**

- 11/11 original SIP/raw/30Min/as-of request keys; 41,861 native rows, including
  17,197/17,197 expected RTH half-hours across 1,327 XNYS sessions.
- 7,935/7,935 complete hourly intervals and 1,327 observed terminal daily closes.
  Zero missing source sessions/slots/windows, conflicting duplicate keys or grid anomalies.
  Extended-session rows are preserved; no raw filling or adjustment occurred.
- Regular sessions have six complete hours plus a 30-minute stub. 2020-11-27
  has three complete hours plus its actual 12:30–13:00 ET stub; no afternoon
  hourly positions. UTC −4/−5, explicit holidays and 13:00 early closes are measured.
- Both 2020-07-01 origins retain all 48 scheduled positions and all per-step
  requirements: 60-hour history and 64 preceding completed daily closes.
  The earliest historical step locks daily history to 2020-06-18.
- Pure research-period raw-window coverage is 2,492/2,492 structurally possible
  origins. Full-source retention is 2,620/2,636 because initial warm-up origins
  lack 48 preceding scheduled steps; this is not a missing-bar failure.
- Causal U1–U5 eligibility is zero: every real row retains UNKNOWN publication
  and unverified split scope. Source completeness does not make vectors valid.
  Staleness with documented publication is not evaluable; no latency is invented.
- Two bounded current process-date queries returned 22 cash distributions and no
  observed split events. The June 2025 ex-date record processes on 2025-07-31.
  This is not certified split absence or exhaustive original action vintage.
  Raw distribution effects remain; no total-return or dividend-cash leg is added.
- Existing stock 168 half-hour gaps remain separate, with all 60 stock pairs unchanged.
  No confirmation returns, labels, predictions, ranking or performance were computed.

Detailed numerators/denominators, year/quarter/month/DST summaries, missingness,
first-July requirements and native training traces: source_qa_full_period.json.
Holiday and research-origin additions: source_qa_calendar_retention.json.
Manifest terminal hashes matched actual canonical journal receipts:
archive_integrity_final.json and transport_budget_reconciliation.json.
Resume was exercised under a GET-that-raises mock, with unchanged 129-attempt journal.

Primary references: [Alpaca bars](https://docs.alpaca.markets/us/reference/stockbars),
[Alpaca corporate actions](https://docs.alpaca.markets/us/reference/corporateactions-1),
[issuer SPY page](https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-sp-500-etf-trust-spy),
[issuer March 2020 sample](https://www.ssga.com/library-content/announcements/etfs/au/20200320-SPY-Distribution-Announcement.pdf).
Action API dates filter process dates, with no guaranteed original availability.
The sample corroborates March 2020 cash rate, not whole-history certification.
