# Older Out-of-Sample Pre-Gap Pattern Test

- Holdout: **2023-01-01 to 2025-08-31**
- Symbols: **26** (same symbol universe, older unseen dates)
- Gap events >=4%: **155**
- Matched non-gap control dates: **416**

- Score >= 3 within prior 10 sessions: gap **61%**, controls **64%**, separation **-3%**
- Score >= 4 within prior 10 sessions: gap **49%**, controls **56%**, separation **-6%**
- Score >= 5 within prior 10 sessions: gap **40%**, controls **44%**, separation **-4%**
- Score >= 6 within prior 10 sessions: gap **23%**, controls **29%**, separation **-6%**

Score components: EMA20>EMA50, full trend stack, shallow <=8% pullback, within 5% of 60d high, 10d range contraction, EMA20 10d slope >=1%.

This is a genuine older-date holdout: the 2026 observations used to discover the pattern are not used as event dates here.
