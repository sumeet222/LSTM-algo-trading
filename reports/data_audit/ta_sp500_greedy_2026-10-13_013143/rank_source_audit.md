# Gate 1 — historical ranking source audit

**HOLD. No compliant S&P 500 float/market-cap ordering has been authenticated.**
No rank-led Alpaca acquisition occurred; no five-stock universe is verified.

The strongest public historical source found is the [SPY March31 report](https://www.sec.gov/Archives/edgar/data/884394/000119312520156851/d923513dn30d.htm),
also available from [its publisher](https://www.ssga.com/library-content/announcements/etfs/au/annual-report-au-en-gb-spy-20200604.pdf). [SEC filing metadata](https://www.sec.gov/Archives/edgar/data/884394/000119312520156851/0001193125-20-156851-index.htm) dates
it June1,2020, accepted11:22:40, before July1 formation. The snapshot is92 days
older than formation. We extracted505 named security values and reconciled their
sum exactly to the report's $235,256,200,309 common-stock total. Nine wrapped
security names were joined; no row values were invented. The publisher PDF is
185281 bytes, SHA256 `9b8bb98362d7141237a8120fce403919eac34cef0f8fc08ecae7000b11ef162e`.

It provides **fund shares and holding values**, not issuer float shares, issuer
market capitalizations or certified S&P constituent weights. Per-security ticker,
security identifier and GICS fields are absent. Its aggregate industry breakdown
does not identify each security's historical sector. March holdings also do not
certify July1 membership after intervening changes. Accordingly the numerical
fund-weight order is a concrete **proposed fallback**, not the requested verified
index ordering or a secretly approved market-cap estimate.

The CSV retains all505 historical securities, including later renamed, acquired
and delisted companies. Proposed duplicate-class handling retains the largest
disclosed class per named issuer, ties by exact name, yielding500 issuers. Neither
class values nor excluded-class weights are added to the retained security or
renormalized. Tickers/sectors remain NOT_VERIFIED except the explicit AAPL anchor.
No current membership or market caps were imported to fill these unknowns.

Public metadata research checked the historical fund report, filing metadata,
publisher mirror and searches for authoritative2020 S&P weights. No complete
authorized float-cap/market-cap table with the necessary identity/sector evidence
was authenticated. This is a bounded research finding, not a claim that licensed
historical index data cannot exist. Direct SEC transport was blocked403; the
publisher mirror succeeded200. These are public-document requests, not Alpaca
entitlement failures or charged historical-bar attempts.

The report is publicly readable, but no redistribution license was acquired.
Only derived numerical/name facts, citations and hashes enter this repository;
the full copyrighted PDF remains temporary/local. ETF holdings were not treated
as official index data merely because SPY tracks the S&P 500.

Prompt §1.2 requires stopping before rank-led acquisition when a defensible
ordering cannot be established. The frozen rule therefore binds the proposal
SHA with live acquisition disabled. The earlier29-name outage and1340/1502
bound do not prove failure of the much larger S&P candidate search.
