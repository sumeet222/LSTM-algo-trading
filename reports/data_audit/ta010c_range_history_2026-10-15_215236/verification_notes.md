# Verification notes

Final focused run: 36 passed, 0 failed, in 75.61 seconds. No legacy training suite ran.
The earlier combined run had 35 passed / 1 failed because the new oracle counted
Plotly 6's encoded ndarray dictionary keys instead of volume samples. The corrected
oracle narrows the real trace to go.Bar and checks every volume value against source.
That isolated test passed, then all 36 passed. An initial AppTest attempt overlapped
visualization reader-binding edits; the coherent binding rerun passed all 13 new tests.
Initial Pylance diagnostics were resolved through validated numeric narrowing,
Sequence covariance and explicit pandas argument bounds; no severity/stub/exclusion changes.
Final installed Pylance: 207 owned files, 0 errors / 0 warnings.
Sandbox localhost binding was denied; the approved outside-sandbox smoke and focused
socket tests passed. Bare Streamlit-context and sandbox Arrow CPU-info warnings are
runtime environment messages, not Pylance diagnostics or fabricated market observations.
No native browser drawing/screenshot, human editor refresh or clean-machine rehearsal claimed.
