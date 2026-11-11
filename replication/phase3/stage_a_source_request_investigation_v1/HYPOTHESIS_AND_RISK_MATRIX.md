# Hypotheses, classification and risks

Status: **STOP_AWAITING_HUMAN_DECISION**. Classification **B**, with the evidence limits below. Ranking reflects explanatory plausibility and evidential strength, not invented probabilities.

| Rank | Required hypothesis | Status | Evidence and disposition |
|---:|---|---|---|
|1|3. Bypass/cache/different path/late refactor|UNRESOLVED|`boundary.py` observed mtime23:41:02 is later than source-build/contract receipt metadata. `prepare.py:25` has a documented saved-geometry branch; later training/recovery use it. A late insertion of recording could explain no requests, but no earlier source snapshot or function-at-use hash proves that change. Exit snapshots have one `boundary` alias; transient cache/version differences remain possible.|
|2|7. Receipts are insufficient|SUPPORTED|All39 valid receipts omit argv/start/end/event times/read modes/stacks; zero custom events; import hashes collected later. This is the directly established limit, not itself a physical cause.|
|3|6. Uncovered artifact builder|SUPPORTED in the narrow request-coverage sense|PID49485 has builder outputs and contract-receipt events; `preflight_execution_001.log` reaches geometry before the M2 error. Its native source requests are uncovered. This does **not** establish a hidden alternate builder or foreign source; later consumer opens cannot fill that gap.|
|4|4. Late hook/flush/lifecycle|UNRESOLVED as historical runtime; simple frozen explanation refuted|Inspected entries register before reads and direct inserts do not depend on `_audit`. Existing successful and interrupted runs serialize valid receipts. Freeze-only unregister cannot remove prior process events. No recorded exact registration/flush timeline rules out every earlier runtime difference.|
|5|1. Logging not implemented/no emission|REFUTED for frozen source; historical version unresolved|`boundary.py:92` implements a direct dictionary event. Absence of `sys.audit` is not absence of logging. Preparation-time implementation is not independently pinned.|
|6|2. Hook filtered/postrun omitted custom events|REFUTED as cause of missing underlying receipts|Direct insertion bypasses hook filter; `receipt():71` serializes all keys; zero requests already in raw receipts. Separately, postrun admission checking is too weak and fails to detect missing event types; that explains overstated coverage, not omission.|
|7|5. Different event name/key collapse|REFUTED for available recorded/frozen path|Complete exact-name recount finds only four built-in/denied names. Key includes event name and path, so custom requests cannot merge with `open`. No inspected caller renames the event. Earlier unrecorded versions are not reconstructable.|

## Why B rather than A, C or D

**Not A:** No concrete cause of the missing direct insertions is established. The postrun validation weakness is real, but does not identify why requests are absent. Mtime is not a historical code diff.

**B:** Positive bounded lineage support includes actual saved expected/actual aggregation values, independently checked arithmetic for2,272 assertions/284 specimens, consistent full-source row totals,174 monthly extraction records,20 matching role-geometry tuples, a builder output footprint, a separate code/synthetic review, and later same-artifact consumer footprints. These are more than manifest/import-lock declarations. The chain is coherent and partially evidenced, not universally attested. Mechanistic review plus saved content does not independently authenticate every source-derived numeric value.

**Not C on current evidence:** We do not find affirmative inconsistent source content or an unexplained alternate source chain, and the positive bounded witnesses above materially support the intended lineage. This classification would change if human review requires universal contemporaneous reader identity as a prerequisite, or new evidence reveals incompatible source/geometry content. B is not an exception approval or a claim that source uncertainty is scientifically immaterial.

**Not D:** No successful forbidden access or original-helper import is established. The two recorded denials are blocked synthetic probes. Absence of observed bad access is not proof that unrecorded native access was impossible.

## Separate risk dimensions

| Dimension | Supported conclusion | Remaining uncertainty / consequence |
|---|---|---|
|File integrity|Prior qualified gate freshly verified232 non-exempt payload files,348 sources,80 protected files and5 byte-identical replay tables. This investigation reverified only69 pertinent receipt/source/document hashes and prior Phase3 evidence.|No renewed348-source scan was performed. Byte identity is not provenance-at-use. The separately authorized metadata exception remains visible.|
|Source/derived lineage|Literal sources and transformation paths, bounded numerical witnesses, monthly counts, geometry checks and observed output/consumer footprints support the intended chain.|No per-native-read event, per-read digest or complete independent real-data reconstruction binds every input value to the final geometry.|
|Isolation/leakage|Recorded module origins and admitted paths show no observed forbidden access; code structure blocks original namespace imports under stated conditions.|Procedural boundary lacks exhaustive native/syscall capture. Runtime source version/instance at preparation remains uncertain. No claim of impossible leakage or physical isolation.|
|Confidence in replication evidence|B supports retaining the existing work for human adjudication with explicit provenance limits.|Neither historical numerical replication nor live/causal validity has been evaluated. No original result was opened and no historical comparison occurred.|
|Scientific exception|Only the previous `.DS_Store` exception is authorized.|Accepting this separate provenance limitation would require a new explicit human decision. Even such acceptance must separately authorize any later unseal.|

Known scientific limitations remain unchanged: inherited preprocessing, nominal versus assumed issuance timing, retrospective policies, fixed surviving universe, F09 scoreability, overlap and exploratory reuse. This focused review does not reconsider methods or support trading/comparator claims.

## Human decision needed

Decide whether the documented bounded lineage support is sufficient to accept a **specific unresolved preparation-time request-recording limitation**, or whether additional separately authorized evidence is necessary. Do not infer permission to regenerate receipts, rerun preparation, alter frozen code, fit models or unseal originals. Current disposition stays STOP_AWAITING_HUMAN_DECISION.
