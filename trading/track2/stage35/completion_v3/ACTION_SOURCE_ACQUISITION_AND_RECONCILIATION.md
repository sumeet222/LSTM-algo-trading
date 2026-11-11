# Actual acquisition and reconciliation

All requests were predeclared in ACTION_SOURCE_PLAN_V3 and numbered bounded
primary/boundary amendments. Exact requested endpoints, queries, UTC retrieval,
HTTP attempts, original content SHA256 and redacted stored-payload SHA256 are in
`audits/*.receipt.json`. No account was created, paid feed used, package installed,
broker endpoint called, key solicited or credential logged. Existing environment
credentials authorized Alpaca's market-data action endpoint. Current account
access is proven by returned records, not a claim about every free plan.

| Source | Actual result | Field/coverage limitation |
|---|---|---|
| Alpaca `/v1/corporate-actions` | HTTP200,275 cash rows in first response;3 splits and18 acquirer notices;one page/no next token | Filter/sort is process date, generally payable date; not complete ex-date coverage or PIT announcement time |
| Alpaca processJan–Mar2025 boundary | HTTP200;retain only2 additional ex<=2024 MRK/PEP dividends paidJan2025 | All other2025 events excluded;no2025 prices queried |
| Nasdaq AAPL dividends | HTTP200;16 OOS cash records agree with Alpaca | Ignores requested date filters and returns older/future metadata;quarantine unused metadata and do not expand this probe to20 names |
| Apple issuer history | HTTP200;16 OOS plus4 raw-share2020 cash records | Declared/record/pay/amount/type;no ex-date;amounts explicitly not split-adjusted |
| Finnhub | HTTP401 without configured key | Authentication unavailable;free historical entitlement not established,not a claim that no free feed exists |
| Alpha Vantage | No existing key;request not sent | Access not configured,not a paywall/coverage conclusion |
| Yahoo dividend CSV | Actual HTTP401 in this run;prior V2 HTTP429 retained | No401 retry or limit evasion;bounded429 policy1 retry/2seconds |
| SEC/issuer | Actual cached Merck,JNJ,Apple,Tesla,Boeing,COP documents | Retrospective facts,not historical feed receipt proof;selected factual scope only |

Schema references: [Alpaca actions](https://docs.alpaca.markets/us/reference/corporateactions-1),
[announcements](https://docs.alpaca.markets/us/reference/getcorporateannouncements),
[Finnhub dividend fields](https://github.com/Finnhub-Stock-API/finnhub-go/blob/master/docs/Dividends.md),
[Alpha Vantage](https://www.alphavantage.co/documentation/).
The legacy Alpaca announcement route is broker-scoped/deprecated; it was not
called. These links establish schemas, not returned historical completeness.
Alpaca ingestion/processing delays prevent treating retrospective availability
as observed historical announcement receipt.

Canonical V3 has267 OOS cash events for16 payers,3 splits,1 mandatory special
hold,18 acquirer-information records,1 voluntary exchange notice and8 verified
zero-dividend security-years:298 rows. Cash:16 Apple rows have primary plus
exchange/provider support;251 remain OBSERVED_UNCORROBORATED. No unsupported
record is promoted to verified to clear a gate. The80 ticker/year rows record
unique reconciled cash counts and raw amount sums;AVGO2024 spans a10:1 split and
its unnormalized sum is explicitly not comparable per constant share.

Tesla's FY2024 SEC dividend policy supports historical nonpayment. Boeing's
FY2022 andFY2024 common-stock nonpayment statements jointly cover2021–24.
Do not confuse Boeing's preferred dividends with common-stock distributions.
Amazon/AMD empty feeds and inaccessible/unhelpful FAQs are not zero proof;
their8 security-years remain UNKNOWN with standalone sensitivity templates.
No quarterly amount/date was fabricated. COP has27 cash rows including base and
variable return of cash;distinct components sharing an ex-date are not duplicates
and must not be extrapolated as one fixed regular series.

Actual primary counterexamples:

- [Merck May7 declaration](https://www.merck.com/news/merck-declares-record-date-and-dividend-for-the-organon-co-spinoff/)
  and [June3 completion](https://www.merck.com/news/merck-announces-completion-of-organon-co-spinoff/)
  establish the1-for10 OGN distribution/May17 record. The successful Alpaca feed
  omitted it. OGN valuation,CIL and comprehensive due-bill/basis handling remain
  unresolved;do not insert zero value or classify it as an ordinary dividend.
- [JNJ's alternate investor release](https://www.investor.jnj.com/investor-news/news-details/2023/Johnson--Johnson-Launches-Exchange-Offer-for-Separation-of-Kenvue-Inc/default.aspx)
  establishes a voluntary exchange. A no-election scenario is explicit. The
  original JNJ URL returned an HTTP200 maintenance page,not event evidence.
- The preliminary SEC Organon document has inconsistent record-date language;
  final Merck declaration/completion takes priority. It is not silently merged.
- An HTTP200 issuer HTML footer containing “premium” or “API key” was initially
  misclassified. Parser corrections and original receipts remain in
  PROVIDER_STATUS_REASSESSMENT_V3.json;those pages were not paid-access failures.
- A Boeing2021 PDF response was captured as unparsed text,not used as evidence;
  the verified2021 nonpayment claim uses the correctly retrieved2022 SEC HTML.

The initial sandbox DNS failure was environmental. Authorized network execution
then returned actual data. Provider statuses are based on those real responses.
Source payloads are local caches,ignored from Git; redistribution rights/PIT
certification are not asserted. Reproduction requires the same response hashes
or a separately versioned source vintage; never overwrite these receipts.
