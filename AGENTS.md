# AGENTS.md

## 1. Purpose and scope

This file defines repository-wide instructions for Codex and other coding agents working on this project.

This is a **two-person group research project** shared through GitHub. The final submission must run on a different machine from either developer's local computer. Therefore, portability, reproducibility, Git safety, data integrity, and communication between separate coding sessions are mandatory.

These instructions apply to the entire repository unless a nested `AGENTS.md` adds stricter local rules.

### Instruction priority

When instructions conflict, use this order:

1. Explicit human instruction for the current task.
2. Accepted project/research protocol and frozen experiment definitions.
3. This `AGENTS.md`.
4. Existing repository conventions.
5. General coding preferences.

Do not silently resolve a genuine research-design conflict. Surface it for human review.

---

## 2. Frozen project context

### Core research question

Can one shared LSTM, trained across several liquid U.S. stocks, predict which stocks will outperform their peers over a short intraday horizon, and does adding broad-market information from the course-provided **USA500** improve cross-sectional ranking quality and trading performance after costs?

### Core universe

- Prototype: `AAPL`, `JPM`, `JNJ`, `WMT`, `CAT`.
- Main experiment: about 20 stocks.
- Intended final scope: about 20-30 stocks, subject to data quality and runtime.
- Use pre-specified coverage/liquidity criteria.
- Do not choose stocks because they perform well in the final test.
- Monitor sector concentration and document survivorship bias if a fixed surviving-stock sample is used.

### Required core data

- Hourly U.S. stock OHLCV.
- Course-provided hourly USA500.
- Corporate-action and trading-calendar information.
- Sector labels or equivalent metadata.

Later extensions only when explicitly requested and justified by a research question:

- USATECH or other hourly cross-asset series.
- Rates/Treasury proxies, FX, gold/oil, sector ETFs.
- SPY/SPX option-state features such as ATM IV, IV change, skew, term structure, IV-RV spread, put/call measures.
- Macro data using publication timestamps and vintage/as-released values.
- Attention, dual-stream LSTM, multi-task heads, regime conditioning, cost-aware position heads, learned portfolio allocation.

Do not add advanced components merely because they are available.

### Primary target

For stock \(i\) at decision time \(t\),

\[
r^{(4)}_{i,t} = \log(P_{i,t+4}/P_{i,t})
\]

and the initial cross-sectional target is

\[
y_{i,t}
=
\frac{
r^{(4)}_{i,t}
-
\operatorname{median}_j r^{(4)}_{j,t}
}{
\operatorname{MAD}_j(r^{(4)}_{j,t})+\epsilon
}.
\]

Interpretation: predict whether stock \(i\) will outperform or underperform the typical eligible stock over the next four trading hours.

Future returns are **labels only**. They must never enter features, eligibility decisions, normalization parameters, portfolio inputs, or any state available at decision time.

Do not replace the primary target with raw future price unless explicitly requested as a diagnostic. Any raw-price diagnostic must be compared with the persistence baseline

\[
\hat P_{t+h}=P_t.
\]

### Core timing

- Inputs remain hourly.
- A four-hour target does not mean four-hour bars.
- Begin with decision times that leave four complete trading hours before the close.
- If decisions are hourly, overlapping four-hour positions must use an explicit exposure rule such as staggered sleeves with a fixed total exposure budget.
- Apply a realistic execution lag: no trade may use a bar before that bar is complete.

### Core model sequence

Minimum controlled comparison:

1. Momentum/ranking baseline.
2. Ridge regression with comparable lagged information.
3. Shared stock-only LSTM.
4. Shared stock + USA500 LSTM.

The main research comparison is **stock-only shared LSTM vs. stock + USA500 shared LSTM**, holding target, dates, execution rules, stock features, tuning budget, and evaluation conventions fixed.

Initial LSTM controls should remain bounded:

- 1-2 LSTM layers.
- Hidden-width grid such as 32/64/128.
- Dropout around 0-0.3.
- Early stopping.
- Gradient clipping if needed.
- Small learning-rate search.
- Starting lookback near 48 trading observations, with a small pre-declared comparison such as 24/48/96.

Do not run unrestricted architecture search unless humans explicitly approve it.

### Core trading mapping

1. Produce one forecast score per eligible stock.
2. Rank scores.
3. Long top 20%.
4. Short bottom 20%.
5. Leave the middle group untraded initially.
6. Equal weight within each side initially.
7. Fix gross exposure and keep net dollar exposure approximately zero.
8. Explicitly handle overlapping four-hour holds.
9. Apply documented transaction-cost, spread/slippage, and shorting assumptions.
10. Measure market beta and sector exposure.

Portfolio-learning methods are a later research branch. Establish the simple portfolio first.

### Required evaluation

Distinguish predictive accuracy from economic usefulness.

Track appropriate subsets of:

- Huber/MSE/MAE.
- Spearman rank IC, mean IC, ICIR.
- Relative-target sign accuracy.
- Absolute direction accuracy if a direction task is added.
- Forecast-quintile returns and monotonicity.
- Gross/net returns.
- Annualized volatility and Sharpe.
- Maximum drawdown.
- Turnover and cost drag.
- Long/short contribution.
- Market beta, sector exposure, concentration.
- Multiple seeds.

Testing must include:

1. Chronological train/validation/test.
2. Purging labels that cross split boundaries.
3. Training-only fitting of scalers, clipping, imputers, and learned transforms.
4. Pipeline freeze before final test.
5. Walk-forward out-of-sample evaluation after the baseline train/validation/test analysis.
6. At least one permutation/null test that destroys meaningful feature-target timing while preserving appropriate marginal/cross-sectional properties where feasible.
7. Where computationally feasible, repeat model fitting and hyperparameter selection inside the permutation procedure.

Never use the final test set to choose features, architecture, thresholds, costs, horizons, or hyperparameters.

---

## 3. Non-negotiable engineering principles

### 3.1 Machine independence

Committed code must run on another supported machine after cloning and following documented setup steps.

Never depend on:

- Developer-specific absolute paths.
- Files existing only in Desktop/Downloads/home folders.
- IDE-only state.
- Undocumented environment variables.
- Manually edited intermediate datasets that cannot be reproduced.
- Undeclared local packages.
- Untracked models/caches required for execution.

Use:

- `pathlib.Path`.
- Project-relative or configured paths.
- Version-controlled configuration.
- Environment variables only for secrets or intentionally machine-specific locations.
- Reproducible download/preprocessing scripts.
- Explicit dependencies.
- Platform-neutral Python whenever possible.

### 3.2 Reproducibility

Any reported experiment should be reproducible from:

- Git commit.
- Config file or complete CLI invocation.
- Seed/seed list.
- Data provenance/version.
- Documented environment/dependencies.

Important research parameters must not exist only as notebook state.

### 3.3 Safety over convenience

Do not use destructive Git or file operations simply to obtain a clean state.

If a safe automatic action is uncertain, stop and report the situation.

### 3.4 Research traceability

Do not silently change:

- Universe.
- Target.
- Lookback.
- Horizon.
- Decision times.
- Splits.
- Cost assumptions.
- Feature definitions.
- Eligibility rules.
- Trading mapping.
- Seed policy.
- Search space.
- Metric definitions.

---

## 4. Recommended repository structure

Respect an established repository structure. Do not reorganize working code without approval.

For a new repo, prefer something like:

```text
.
├── AGENTS.md
├── README.md
├── pyproject.toml / requirements files
├── .gitignore
├── .env.example
├── configs/
├── data/
│   ├── README.md
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
├── notebooks/
├── reports/
│   └── codex_sessions/
├── scripts/
├── src/
│   └── <project_package>/
├── tests/
└── artifacts/
```

Rules:

- Reusable logic belongs in `src/`.
- Notebooks are not the sole implementation of important logic.
- `scripts/` contains reproducible entry points.
- Large raw data, caches, checkpoints, and generated artifacts should normally be gitignored.
- `data/README.md` should explain sources and reproduction.


---

## 5. Dependency and environment policy

The repository must have one documented authoritative setup route.

- Declare direct dependencies explicitly.
- Pin or constrain versions enough for reproducibility.
- Keep machine-readable environment specification in Git.
- Keep lock files synchronized when used.
- Do not rely on globally installed packages.
- Do not depend on an IDE for execution.
- Avoid unnecessary heavy dependencies.

When adding a dependency:

1. Explain why existing dependencies are insufficient.
2. Add it to the dependency specification.
3. Update setup docs if needed.
4. Mention it in the session report.
5. Test a representative import or execution path.

The README should eventually include a clean-machine setup route such as:

```bash
git clone <repo>
cd <repo>
python -m venv .venv
python -m pip install -U pip
python -m pip install -e .
python -m pytest
```

Exact commands may differ if the team adopts another environment manager.

---

## 6. Path and file handling

- Use `pathlib.Path`.
- Do not infer project root from a username/home directory.
- Use explicit config paths or a robust project-root helper.
- Create output directories idempotently.
- Never overwrite raw/source data in place.
- Write derived data to separate locations.
- Validate required columns, dtypes, timestamp parsing, and timezone assumptions.
- Fail with useful errors when required inputs are absent.
- Use safe replacement patterns for important generated files where interruption could corrupt the only copy.

---

## 7. Data integrity and provenance

### Raw data are immutable

Never:

- Hand-edit raw rows.
- Backfill by editing raw files.
- Overwrite raw with processed data.
- Delete raw data during ordinary preprocessing.

Corrections belong in code with documented rationale.

### Record provenance

For each external dataset preserve, where relevant:

- Provider/source.
- Retrieval date.
- Symbols.
- Date range.
- Frequency.
- Timezone.
- Regular/extended-session policy.
- Corporate-action adjustment policy.
- API/feed tier if it changes coverage.
- Material request parameters.
- Known limitations.

If raw data cannot be committed, commit the downloader/config/metadata needed to recreate it.

### Market-time correctness

Be explicit about:

- UTC vs U.S. Eastern.
- Daylight-saving changes.
- Regular trading hours.
- Holidays/early closes.
- Overnight USA500 observations.
- Missing bars.
- Splits/corporate actions.
- Entry/exit timestamp convention.

Never forward-fill prices through non-trading hours merely to force alignment.

### Leakage checks are mandatory

- Rolling features use only data at or before decision time.
- Time-series standardization is fitted on training only.
- Cross-sectional transforms at `t` use only information observable at `t`.
- Future returns are labels only.
- Macro features use publication timing/vintage values where relevant.
- Options features use historical values actually available at that timestamp.

---

## 8. Feature-engineering policy

Prefer stationary or approximately scale-invariant features.

Examples:

- 1h, 2h, 4h, 8h, 24h log returns.
- Cumulative returns over selected windows.
- Volatility-scaled returns.
- Rolling realized volatility.
- Short/long volatility ratios.
- Absolute-return z-scores.
- Downside/upside semivolatility where reliable.
- Normalized high-low range.
- Open-close return.
- Close location within range.
- Volume and dollar-volume z-scores.
- Volume change.
- Return × relative-volume interactions.
- Normalized moving-average distance.
- Rolling high/low distance.
- Limited RSI/MACD-style transforms.
- Rolling beta/correlation to USA500.
- Stock return minus market return.
- Sector-relative return.
- USA500 multi-horizon return, volatility, trend, normalized drawdown.

Do not generate hundreds of indicators because a library exposes them.

Each feature block should correspond to a controlled research hypothesis.

---

## 9. Optional later prediction tasks

Do not implement these automatically.

### Future realized volatility

Possible target:

\[
RV^{(4)}_{i,t}
=
\sqrt{\sum_{h=1}^{4} r_{i,t+h}^{2}}.
\]

A stabilized target such as `log(RV + eps)` may be preferable.

Use simple volatility baselines such as historical/EWMA persistence and, if appropriate, HAR-like or GARCH-family benchmarks.

### Direction

\[
d_{i,t}=1\{r^{(4)}_{i,t}>0\}.
\]

Do not confuse relative outperformance with positive absolute return.

### Relative rank

A rank/percentile target may be tested when approved and should be compared fairly with the standardized relative-return target.

### Options implied volatility

If reliable timestamped historical options data become available, option-IV forecasting or options-state conditioning may be added later. Start with market-level SPY/SPX features before full stock-option chains.

---

## 10. Experiment configuration and artifacts

Research experiments should be configuration-driven where practical.

Configs should capture material choices such as:

- Universe.
- Dates/splits.
- Horizon.
- Lookback.
- Feature blocks.
- Target.
- Model family.
- Architecture.
- Dropout.
- Optimizer/learning rate.
- Batch size.
- Early stopping.
- Seed.
- Transaction costs.
- Portfolio quantiles.
- Holding/rebalance rule.
- Exposure constraints.
- Metrics.

Do not silently overwrite prior reported experiment outputs.

Each important experiment should, where practical, record:

- Experiment ID.
- Start/end time.
- Git SHA.
- Config path/snapshot.
- Seed.
- Python/package versions.
- Data provenance identifier.
- Key metrics.
- Completion/failure status.

Large checkpoints/artifacts may remain untracked, but small metadata/config/result tables needed to interpret reported results should be tracked when appropriate.

---

## 11. Testing requirements

Automated tests should cover research-critical behavior.

### Portability

- No username-specific paths.
- Imports work without manual `PYTHONPATH`.
- Output directories are created safely.
- Clean-checkout commands work as documented.

### Data correctness

- Expected columns/dtypes.
- Timestamp ordering/uniqueness.
- Timezone/calendar alignment.
- Corporate actions.
- Missing-bar policy.
- Raw-data immutability.

### Leakage and target alignment

- Features at `t` use no future data.
- Four-hour label matches intended entry/exit timing.
- Labels crossing split boundaries are purged.
- Training transforms do not fit validation/test.
- Cross-sectional target uses only eligible names.
- Near-zero MAD is handled explicitly.

### Portfolio logic

- Top/bottom selection.
- Long/short weights.
- Gross/net exposure.
- Overlapping sleeves/exposure budget.
- Execution lag.
- Transaction costs exactly once.
- Turnover calculation.

### Reproducibility

- Fixed seeds reproduce deterministic components where feasible.
- Config loading preserves research parameters.

When research-critical code changes, update tests.

Do not finish with known failing tests unless the task is explicitly about an unresolved failure; document any remaining failure prominently.

---

## 12. Coding standards

### Python

- Keep the repository `.venv/bin/python` interpreter and installed Pylance basic severity.
- Every Python package must end with zero reproducible error-level Pylance/Pyright
  diagnostics over all project-owned Python, including new files. Check incrementally
  after logical code batches and over the full project at completion.
- Do not hide diagnostics using reduced severity, exclusions, ignore directives,
  broad `Any`, unjustified casts, Ruff `noqa`, or weakened tests. Preserve runtime behavior.
- Every session report must include the exact static-check command, zero-error summary
  and editor verification instructions. Interpreter/stub parity failures or genuine
  residual errors require HOLD; final editor Problems refresh is human-confirmed.

- Prefer small testable functions.
- Use type hints for public/reused interfaces where practical.
- Add concise docstrings to reusable functions/classes.
- Comment non-obvious timing, leakage, portfolio, and transform-fitting logic.
- Use meaningful names.
- Avoid hiding important assumptions in opaque one-liners.
- Raise informative exceptions for violated research assumptions.
- Avoid silent coercion of timestamps, missing values, and schemas.

### Notebooks

Use notebooks for exploration/visualization/presentation, not as the sole source of production logic.

Reusable logic should move to `src/` and receive tests.

### CLI/scripts

Important workflows should eventually have reproducible commands for:

- Data download.
- Data audit.
- Feature/label generation.
- Training.
- Evaluation.
- Backtesting.
- Walk-forward analysis.
- Null/permutation experiments.

Major CLIs should provide useful `--help`.

---

## 13. Credentials and secrets

Never commit:

- API keys.
- Passwords.
- Tokens.
- Private credential-bearing URLs.
- Secret `.env` files.
- Cloud credentials.
- Personal account identifiers.

Use environment variables.

Maintain `.env.example` or equivalent documentation with placeholders only.

Example:

```text
ALPACA_API_KEY=
ALPACA_API_SECRET=
```

Code must fail clearly if required secrets are missing.

Never print secrets in logs or session reports.

---

## 14. Git collaboration and local-work safety

This repository is shared by two people. Protecting local and remote work is mandatory.

### Start every Codex session with repository inspection

Before editing:

1. Read this `AGENTS.md`.
2. Read the most recent relevant files in `reports/codex_sessions/`.
3. Inspect:

```bash
git status --short --branch
git branch --show-current
git rev-parse HEAD
git remote -v
git fetch --all --prune
```

4. Determine whether the branch is ahead, behind, or diverged.
5. Identify uncommitted/untracked work.

Record starting branch and SHA in the session report.

### Never start with a blind `git pull`

Prefer `git fetch` first.

If the tree is clean and the branch is only behind upstream, prefer:

```bash
git pull --ff-only
```

or equivalent fetch + fast-forward.

If branches diverged, do **not** auto-rebase/reset/force-merge/discard. Surface the condition for human review unless explicitly authorized.

### Dirty working tree

If uncommitted work exists:

- Do not pull/merge/rebase over it.
- Do not reset/discard it.
- Inspect and report it.
- Prefer committing intentional work before integration.
- Use `git stash` only with a clear, documented purpose.
- Never assume unknown untracked files are disposable.

### Destructive commands require explicit authorization

Examples:

```text
git reset --hard
git clean -fd
git clean -fdx
git checkout -- .
git restore .
git push --force
git push --force-with-lease
```

Do not rebase published/shared history without coordination.

### Branches

Prefer short-lived branches:

```text
feat/data-pipeline
feat/shared-lstm
exp/usa500-conditioning
fix/target-alignment
docs/session-reporting
```

Keep the default branch runnable.

### Commits

Commits should be focused and descriptive.

Do not mix unrelated refactors, model changes, data-format changes, and formatting cleanup unless inseparable.

Do not rewrite another collaborator's published commits without coordination.

### Push safety

If push is rejected:

1. Do not force push.
2. Fetch.
3. Inspect divergence.
4. Reconcile carefully or ask for review.

### Merge conflicts

- Understand both sides.
- Preserve intentional work from both contributors.
- Do not choose whole-file "ours"/"theirs" merely for speed.
- Rerun tests.
- Document meaningful conflict resolution in the session report.

Session reports are an additional audit layer, not a replacement for Git.

---

## 15. Recommended GitHub workflow

For substantive changes:

1. Work on a named branch.
2. Fetch before starting and before pushing.
3. Keep commits focused.
4. Push the branch.
5. Use a Pull Request when practical.
6. Confirm tests pass.
7. Merge without rewriting collaborator history.
8. Delete branches only after safe merge.

Direct documentation-only commits may be acceptable if the team agrees, but the session-report rule still applies.

Branch protection on the default branch is recommended when practical.


---

## 16. Mandatory Codex session workflow

### Before coding

- Read `AGENTS.md`.
- Read latest relevant session reports.
- Inspect Git/repository state.
- Identify the relevant research config/protocol.
- Identify likely files to change.
- Check for contradictions.
- Do not broaden scope silently.

### During coding

- Make the smallest coherent change.
- Preserve compatibility unless change is intentional.
- Add/update tests with research-critical changes.
- Keep raw data immutable.
- Avoid unrelated cleanup.
- Keep paths machine-independent.
- Update docs/configs if interfaces change.
- Track important new functions/classes/config keys for the report.

### Before ending

- Run relevant tests.
- Run a smoke test where feasible.
- Review `git diff`.
- Review `git status`.
- Check for secrets, large generated files, and machine-specific paths.
- Create the mandatory session report.
- Ensure the report itself appears in `git status`.
- If authorized to commit, include the report with the corresponding changes.
- If not authorized, leave exact commit/push guidance and report the uncommitted state.

A coding session is **not complete** until its session report exists.

---

## 17. Mandatory session report after every Codex session

### Location

```text
reports/codex_sessions/
```

### Naming

Recommended:

```text
YYYY-MM-DD_HHMMSS_<branch-or-topic>_<short-slug>.md
```

Examples:

```text
2026-10-07_011500_feat-data-pipeline_alpaca-download.md
2026-10-08_164200_exp-usa500_conditioning.md
```

Never overwrite an older session report.

If a report contains an error, create a new correction/follow-up report referencing it.

### Purpose

The report is:

- Technical handoff between group members.
- Handoff between Codex sessions.
- Secondary audit trail beyond Git.
- Map of important files/interfaces.
- Record of research changes.
- Reproduction aid.
- Warning system for incomplete or merge-sensitive work.

Create a report even if:

- The session failed.
- Only documentation changed.
- No code was implemented.
- The work is partial.

### Required template

```markdown
# Codex Session Report

## 1. Session metadata

- Date/time:
- Contributor / session:
- Task requested:
- Branch:
- Starting commit:
- Ending commit (if committed):
- Working tree at start:
- Working tree at end:
- Related issue/PR (if any):

## 2. Executive summary

What was accomplished and current project state.

## 3. Research/protocol impact

- Research question affected:
- Target/horizon changes:
- Feature-set changes:
- Universe/data changes:
- Split/validation changes:
- Trading/backtest changes:
- Hyperparameter/search-space changes:
- Whether final-test protocol was touched:
- If nothing research-relevant changed, say so explicitly.

## 4. Files created

For every file:
- Path.
- Purpose.
- Type of file.
- Important interfaces/assumptions.

## 5. Files modified

For every file:
- Path.
- What changed.
- Why.
- Compatibility/downstream effect.

## 6. Files deleted, renamed, or moved

For every item:
- Old path.
- New path if applicable.
- Reason.
- Import/config/path updates required.

If none, say so.

## 7. Critical functions, classes, variables, and config keys

For important new or materially changed interfaces:
- Name.
- File.
- Signature/type.
- Purpose.
- Inputs.
- Outputs.
- Side effects.
- Invariants.
- Timing/leakage assumptions.
- Callers/dependencies.

## 8. Data/schema/provenance changes

- Sources.
- Columns/dtypes.
- Timestamp/timezone assumptions.
- Corporate-action rules.
- New paths.
- Data version/provenance.
- Rebuild/migration requirements.

## 9. Dependency/environment changes

- Packages added/removed.
- Version changes.
- Environment variables.
- Setup-document changes.

## 10. Commands and tests run

List important commands exactly where practical.

For each:
- Result.
- Pass/fail counts if known.
- Warnings.
- Runtime issues.

Never claim a test passed if it was not run.

## 11. Experiment/results summary

If experiments ran:
- Experiment ID/config.
- Data window.
- Universe.
- Model/seed.
- Predictive metrics.
- Trading metrics.
- Train/validation/test/walk-forward status.
- Exploratory vs report-eligible status.
- Artifact location.

Do not present exploratory validation results as final conclusions.

## 12. Reproduction instructions

Shortest reliable procedure for another machine/group member:
- Setup.
- Environment variables.
- Required data.
- Commands.
- Expected outputs.

## 13. Git / collaboration status

- Current branch.
- Commits created.
- Uncommitted changes.
- Untracked files.
- Whether remote was fetched.
- Ahead/behind/diverged state.
- Files likely to conflict.
- Recommended PR/merge action.

## 14. Known issues, risks, and limitations

- Failing tests.
- Unverified assumptions.
- Data-quality issues.
- Platform-specific concerns.
- Performance bottlenecks.
- Leakage/research risks.
- Temporary workarounds.

## 15. Decisions requiring human or teammate review

List choices that must not be silently made by the next Codex session.

## 16. Next recommended steps

Prioritized handoff list.

## 17. Artifact inventory

List important:
- plots,
- tables,
- checkpoints,
- logs,
- cached data,
- reports.

State whether each is tracked or intentionally local.
```

### Report quality bar

A collaborator should be able to answer from the report:

- What changed?
- Why?
- Where is the important code?
- What interfaces now exist?
- What tests ran?
- What is safe to do next?
- What remains broken/uncertain?
- Does any local work need protection before pulling/merging?
- Can the change be reproduced elsewhere?

Do not fill reports with low-value line-by-line narration.

Never include secrets.

---

## 18. Communication between Codex sessions

At the start of each new session:

1. Read the newest session report.
2. Read recent reports touching the same component.
3. Inspect the referenced files and Git history/diff.
4. Honor unresolved warnings and human-decision items.
5. Do not undo recent work without understanding why it exists.

When changing a public function, config schema, dataset schema, CLI, or artifact path, update:

- Code.
- Tests.
- Docs/config examples.
- Session report.

---

## 19. Human research control

Codex is an implementation assistant, not an unreviewed experiment designer.

For major empirical experiments, humans should decide or approve:

- Hypothesis.
- Controlled change.
- Primary metric.
- Expected failure mode.
- Go/no-go criterion.
- Exploratory vs confirmatory status.

Useful controlled dimensions include:

- Horizon: 1h/2h/4h/8h.
- Lookback: e.g. 24/48/96.
- Target: standardized relative return vs rank vs direction.
- Return-only vs return+volatility multi-task.
- Feature blocks.
- Shared vs stock-specific model.
- Stock-only vs stock+USA500.
- Capacity/regularization.
- Trading quantile.
- Holding/rebalance rule.
- Equal vs volatility-scaled weights.
- Costs.
- Regime dependence.
- Options-state value.
- Permutation/null robustness.

Never select the "best" configuration by repeated final-test inspection.

---

## 20. Planned research sequence

Unless humans explicitly revise the plan:

### E0 — Data and execution sanity

Five-stock prototype.

Verify timestamps, timezones, sessions, corporate actions, USA500 overlap, missing bars, target timing, entry/exit timing, and simple backtest accounting.

No neural result should be trusted before this passes.

### E1 — Classical baselines

- Momentum/ranking.
- Ridge with comparable lagged information.

### E2 — Shared stock-only LSTM

Evaluate under identical target/timing/trading conventions.

### E3 — Main test: add USA500

Keep everything else fixed as much as possible and measure incremental value.

### E4 — Feature/memory ablations

Small controlled comparisons only.

### E5 — Volatility branch

Forecast future realized volatility, then optionally add a return+volatility multi-task model.

Test whether predicted volatility helps risk scaling and trading.

### E6 — One justified model extension

Choose one at a time, e.g. temporal attention **or** separate market-state LSTM.

### E7 — Options-state branch

Only with reliable timestamped options history. Start market-level.

### E8 — Robustness

- Multiple seeds.
- Walk-forward OOS.
- Cost sensitivity.
- Regime analysis.
- Permutation/null test.

### E9 — Portfolio branch

Only after alpha forecasts are frozen.

Compare:

1. Equal weights.
2. Inverse-volatility or score/predicted-volatility weights.
3. Constrained classical optimizer.
4. Only then differentiable/learned allocator.

Use the same frozen alpha forecasts when comparing allocators.

---

## 21. Portfolio-learning extension policy

Do not begin with a learned allocator.

A later constrained portfolio problem may take the form

\[
\max_w
\quad
w^\top \hat\mu_t
-
\lambda w^\top\hat\Sigma_t w
-
\gamma \|w-w_{t-1}\|_1
\]

subject to

\[
\sum_i w_i=0,
\qquad
\|w\|_1\le G,
\qquad
|w_i|\le w_{\max},
\]

with optional sector/beta limits.

If a learned/differentiable allocator is later used:

- Compare it to equal weighting and a constrained classical optimizer.
- Use the same frozen alpha forecasts.
- Include previous weights and transaction costs where appropriate.
- Do not attribute allocation gains to predictor quality.

---

## 22. Definition of done

Before declaring a task complete, verify as applicable:

- Requested behavior implemented.
- Machine-independent paths.
- Dependencies declared.
- No secrets.
- Raw data not mutated.
- Research assumptions not silently changed.
- Relevant tests pass.
- Smoke test run where feasible.
- Docs/config updated.
- `git diff` reviewed.
- `git status` reviewed.
- Mandatory session report created.
- Report contains unresolved issues and exact Git/collaboration state.
- Another group member can reproduce the change with documented external data/credentials.

---

## 23. Hard prohibitions

Without explicit human authorization, do not:

- Delete/overwrite unknown local work.
- `git reset --hard`.
- Destructive `git clean`.
- Force push.
- Rebase shared history.
- Resolve divergence by discarding one side.
- Commit credentials.
- Hard-code a developer machine path.
- Modify raw vendor/course data in place.
- Tune on the final test.
- Use future information in features.
- Silently change target, timing, costs, splits, or universe.
- Select stocks based on final-test performance.
- Add large artifacts unintentionally.
- Replace the core experiment with a more complex model merely because exploratory validation looks better.
- Hide materially important negative/failed results.

---

## 24. Final portability rehearsal

Before final submission:

1. Clone the repo into a new location with no dependence on existing developer folders.
2. Create the environment using repository instructions.
3. Supply only documented secrets/data.
4. Run tests.
5. Run the smallest end-to-end pipeline from raw/retrieved data through features/model/evaluation.
6. Run final documented submission command(s).
7. Verify outputs use project-relative/configured locations.
8. Record the rehearsal in a Codex session report.

The final submission must not depend on hidden manual steps known only to one group member.
