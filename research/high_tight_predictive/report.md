# HIGH_TIGHT Predictive Validation

- Window: **2022-01-01 to 2025-12-31**
- Symbols: **26**
- All eligible stock-days: **25609**
- HIGH_TIGHT stock-days: **5538**

- Power gap >=15% within next 10 sessions after HIGH_TIGHT: **0.33%**
- Same outcome on non-HIGH_TIGHT stock-days: **0.47%**
- Relative lift: **0.69x**

- Non-overlapping HIGH_TIGHT episodes: **457**
- Episode hit rate within next 10 sessions: **0.22%**

## Interpretation

- This is the key forward-style test: stand on each historical day, identify HIGH_TIGHT using only past data, then ask whether a >=15% opening gap occurs in the next 10 sessions.
- A visually appealing pattern is only useful if the forward hit rate and lift are meaningfully above the ordinary stock-day baseline.
