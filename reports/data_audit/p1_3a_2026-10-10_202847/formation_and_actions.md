# P1.3A — formation and actions evidence

Formation date is **2020-07-01**. D1 requires trailing **60 exchange sessions' average dollar volume ≥$50 million**. The required window is **2020-04-06–2020-06-30**: 300 distinct daily observations for five originals, or 600 if all backups are separately authorized for screening. P1.1 verified physical presence on the first date for each original; only AAPL's numerical daily row was retained. This cannot establish an average or a contemporaneously observable screen.

| Candidate | Role / sector-preserving pair | Policy sector label | 60-session liquidity | USA500 membership |
|---|---|---|---|---|
| AAPL | Original / MSFT backup | Information Technology | BLOCKED | UNKNOWN-BLOCKED |
| JPM | Original / BAC backup | Financials | BLOCKED | UNKNOWN-BLOCKED |
| JNJ | Original / MRK backup | Health Care | BLOCKED | UNKNOWN-BLOCKED |
| WMT | Original / COST backup | Consumer Staples | BLOCKED | UNKNOWN-BLOCKED |
| CAT | Original / HON backup | Industrials | BLOCKED | UNKNOWN-BLOCKED |
| MSFT | Backup for AAPL | Information Technology | NOT_RUN; inputs missing | UNKNOWN-BLOCKED |
| BAC | Backup for JPM | Financials | NOT_RUN; inputs missing | UNKNOWN-BLOCKED |
| MRK | Backup for JNJ | Health Care | NOT_RUN; inputs missing | UNKNOWN-BLOCKED |
| COST | Backup for WMT | Consumer Staples | NOT_RUN; inputs missing | UNKNOWN-BLOCKED |
| HON | Backup for CAT | Industrials | NOT_RUN; inputs missing | UNKNOWN-BLOCKED |

Sector labels above reproduce the frozen pairing/coarse policy, not a verified historical sector dataset. Originals have only existing retrospective 30Min QA and the one-day P1.1 sample; backups have no source probe here. **No backup activated.** USA500 identity/membership is unresolved in P1.2, so membership is neither automatically false nor replaceable by S&P membership. D8's high/low liquidity directed pair remains unselected until the same valid formation screen exists.

**Convention decision:** D1 does not specify the daily dollar-volume price statistic. A proposed proxy is raw daily close × matching raw daily share volume, averaged over all 60 valid sessions. That differs from actual traded dollar volume or a VWAP/regular-session aggregation; their price/volume/trade-filter bases must be verified. Never mix adjusted price with raw volume. Correct split price/inverse-volume adjustment preserves the product algebraically, but does not prove historical publication/vintage. The exact daily session/filter definition and a justified current-history-versus-then-available-data assumption need human approval. Missing sessions must not be dropped to shorten the denominator.

## Actions capability and missing treatment

| Input / use | Existing evidence | Missing before production |
|---|---|---|
| Raw minute opens / execution | P1.1 sampled 24 requested AAPL/JPM rows | All-name/date/retry coverage; publication and actual fillability |
| Split OHLC + inverse-share volume / FT0 | Existing SIP/split/30Min store; P1.1 sampled AAPL factor4, JPM factor1 | Complete historical events/share basis; point-in-time adjustment/publication qualification |
| Split events / physical shares | Issuer illustration below; provider documents split types | Actual event IDs/ratios/effective dates and complete all-name history |
| Cash dividends / buy-hold and physical P&L | One P1.1 AAPL metadata record; issuer dates below | Entitlement, ex/record/pay/declaration dates, rate/currency/share basis, short liabilities, receivables/cash/reinvestment policy |
| Event availability / vintage | No guarantee or historical vintage evidence | Historical creation/publication/revisions, corrected/cancelled statuses, complete pagination and coverage |

[Alpaca bars documentation](https://docs.alpaca.markets/us/reference/stockbars) distinguishes raw from split price/volume adjustments; its `asof` parameter maps entities rather than restoring historical vintages. [Corporate-actions documentation](https://docs.alpaca.markets/us/reference/corporateactions-1) supports splits/dividends but uses process-date filtering and does not guarantee timely creation. `data_quality=complete` is not a historical-completeness certificate. Existing access does not certify current SKU/ongoing entitlement. These are public documentation reads, not new authenticated source requests.

Two preselected AAPL illustrations (official pages checked this session): [Apple history](https://investor.apple.com/dividend-history/default.aspx) lists a **4-for-1 split dated2020-08-31**, declared July30, record date August24. It also lists a **$0.77 dividend**, declared2020-01-28, record date February10, payment February13. P1.1's exact API record `23407e01-4eef-4c1e-a2dd-f585c7eabcd0` has cash-dividend rate0.77 and **ex/process date2020-02-07**. Ex date, record date and payment date are different fields, not contradictory interchangeable dates. The prior API response had another page, deliberately unfetched; its sample omitted pay/record dates. Issuer facts corroborate these illustrations, not the complete provider ledger or historical availability.

**Synthetic split check, not a portfolio/backtest:** 10 shares ×$100 +$50 cash =$1,050. A pure4:1 split gives40 shares ×$25 +$50 =$1,050. Adjusted pre/post feature prices both25; pre-volume200 becomes800, so price×volume stays20,000. No cash dividend or fabricated split P&L is added. P1.1's real open rounding residual0.0025 remains a separate uncorrected precision warning.

**Synthetic dividend distinction:** a stipulated $0.77 ex-price drop on10 entitled shares is offset by a $7.70 receivable, not immediate pay-date cash; verified payment later transfers that receivable to cash. This checks algebra only, not an assumed real price drop or chosen vendor/simulator transaction policy. Both isolated checks passed and are recorded in `source_readiness.json`. No production actions ledger was implemented.
