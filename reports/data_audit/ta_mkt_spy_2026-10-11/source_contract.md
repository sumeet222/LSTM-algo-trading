# SPY source contract evidence

Checked 2026-10-11; archive qualification only, scientific status BLOCKED.

- [Alpaca historical bars](https://docs.alpaca.markets/us/reference/stockbars):
  explicit 30Min, SIP, raw, entity-mapping asof=2025-06-30; inclusive request bounds.
  Follow every continuation page, including short responses. Raw applies no adjustment;
  split and dividend adjustments are separate provider policies. No default-feed reliance.
- [Single-symbol endpoint](https://docs.alpaca.markets/us/v1.1/reference/stockbarsingle-1)
  confirms the corresponding SPY stock-bar API; this package reuses the existing multi-symbol
  client with symbols=SPY and fixed historical host.
- [Alpaca FAQ](https://docs.alpaca.markets/us/docs/market-data-faq): bars use the left
  interval boundary; SIP aggregates exchanges; historical entity mapping differs from
  real-time publication. A successful historical GET demonstrates access, not a verified
  subscription tier, redistribution licence or contemporaneous availability.
- [Issuer March 2020 distribution notice](https://www.ssga.com/library-content/announcements/etfs/au/20200320-SPY-Distribution-Announcement.pdf):
  confirms a US-announced SPY distribution with March 20 ex-date. This is issuer evidence
  for one sample, not a complete split/distribution inventory. Raw ETF price returns include
  distribution effects; no cash reinvestment or total-return reconstruction is introduced.

The pilot empirically tests exact half-hour starts before treating native 30Min timestamps
as left boundaries for the reused hourly aggregator. Historical publication remains
UNKNOWN: an archive's period_end or retrieval time must not be assigned to available_at.
SPY is listed on NYSE Arca; the approved XNYS regular-session calendar is reused for the
common equity schedule, not falsely represented as SPY's listing exchange.
No claim of verified absence of splits is made. Corporate-action scope completeness and
consistent split handling remain pending before empirical market features can qualify.
