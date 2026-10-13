# Gate A — finite pool and one selection

Exactly49 names (AAPL+48), exactly20 additions; all245 stock/date samples measured. All49 formation daily samples contain60 unique expected sessions and exceed$50m as a retrospective vendor close×volume proxy. Historical membership, sector certification and publication remain UNVERIFIED. The deterministic rule was published before any new sample GET.

|Symbol|Provisional sector|5-date observed/65|Missing|Longest run|Terminal absent|60-session dollar-volume proxy|
|---|---|---:|---:|---:|---:|---:|
|COST|Consumer Staples|65|0|0|0|$1,068,157,623|
|CMCSA|Communication Services|65|0|0|0|$967,094,222|
|SBUX|Consumer Discretionary|65|0|0|0|$958,658,062|
|HON|Industrials|53|12|12|1|$588,160,936|

- COST beats PEP in Consumer Staples: 0 vs 0 missing keys; 0 vs 0 missing closes. Both are zero-gap; the fixed liquidity tie break selects COST over PEP.
- CMCSA beats DIS in Communication Services: 0 vs 46 missing keys; 0 vs 4 missing closes. The frozen missingness priorities decide before liquidity.
- SBUX beats HD in Consumer Discretionary: 0 vs 36 missing keys; 0 vs 3 missing closes. The frozen missingness priorities decide before liquidity.
- HON beats GE in Industrials: 12 vs 36 missing keys; 1 vs 3 missing closes. The frozen missingness priorities decide before liquidity.

Only three non-Tech sectors have zero-gap sampled candidates. PEP cannot add a fourth sector because COST occupies Staples. HON is the least-bad remaining sector; its12-consecutive gap violates the1–2 preference. The current prompt explicitly authorizes provisional least-missing selection and full acquisition despite this. Selected order COST,CMCSA,SBUX,HON is fixed before bulk; no later quality replacement. GM remains measured in the pool (36 missing keys), never excluded by profitability.
