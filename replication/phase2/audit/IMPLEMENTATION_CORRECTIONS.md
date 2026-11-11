# Visible implementation corrections before fitting

1. Initial contract attempt stopped at the first month calendar-membership assertion. The independently constructed pandas 3 schedule inferred microsecond resolution while canonical timestamps were nanoseconds. Explicit `.dt.as_unit("ns")` now normalizes the schedule before integer timestamp comparison. This was a new implementation unit error, not a source or method change. The original failed log is retained as `contract_execution.log`; subsequent attempts use distinct logs. No features or neural fits had run.

2. Contract attempt 002 was intentionally interrupted during read-only preprocessing after profiling showed timezone-aware `strftime` took 28 seconds for a monthly vector. Replaced that rendering with vectorized local-date conversion, preserving calendar dates and all methods. Attempt 002 log and the profiling receipt are retained. This is not a neural retry: no neural fit occurred.

3. Independent synthetic review caught cancellation in an initially proposed cumulative-prefix rolling mean: a remote value1e16 could erase a later all-one two-position mean. Replaced sum subtraction with bounded window-local summation before any real feature construction. Counts and triple-NaN/regime gates remain unchanged. The mathematical scheduled-window method is preserved.

4. Independent feature review identified that Q2 additionally needs the previous daily U regime to equal the current grid regime; internally homogeneous old-regime U windows must not combine with a current-regime pseudocount after a split. Added this guard under the explicit cross-regime Q1/Q2 prohibition before real feature construction.

5. A synthetic marker-axis test caught a broadcasting error in M2 tensor assembly. Expanded the `[origin,step]` index with a stock axis before selecting `[origin,step,stock]` contexts. This enforces one forecast context throughout each historical window. No real neural fitting had begun.
