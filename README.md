# Daily Market Scanner

Public GitHub Actions runner for:

- US Playbook + VCP
- TSX + HKEX Legacy Playbook + VCP
- Big Zone Scanner (US + TSX + HKEX)
- US Volatility Compression Scanner (direction-neutral pre-expansion ranking)

Scheduled Monday-Friday. Results are saved as GitHub Actions artifacts.

## US volatility-compression scanner

`volatility_compression_scanner.py` ranks the current
`data/us_1b_universe.txt` list by how tightly volatility and price structure
have contracted. It does not predict direction. A directional expansion is
reported only when the latest close exits the prior 10-session range and true
range is at least 1.2 times the preceding five-session median.

The score combines HV20, ATR14%, Bollinger-band width, SMA 5/10/20 convergence,
short-vs-medium true-range contraction, optional volume contraction, 10-session
coil width and NR7. Results are written to
`volatility_compression_results/us/` and the scheduled workflow publishes the
latest files under `latest/volatility_compression_us/`.

The actionable `watch.csv`, `prebreakout_watch.csv`, `top50.csv` and
`tradingview.txt` apply a second-stage pre-breakout quality gate. Candidates
must be liquid, have RS percentile of at least 70, sit within 5% below to 1%
above an unbroken 20-session pivot, remain close to the 50-day average, and
avoid recent event gaps or already-extended runs. Event-gap shelves are
quarantined for 60 sessions. The gate also rejects unusually motionless price
pegs and new plateaus more than 12% above the preceding 21-to-125-session price
structure; these patterns commonly occur around cash takeovers and other
one-off events rather than before an organic breakout. Raw compression
matches remain available in `compression_watch.csv`; excluded names and exact
reasons such as `POST_GAP_COIL`, `EVENT_PRICE_PEG`, and
`DETACHED_FROM_PRIOR_STRUCTURE` are written to `rejected_compression.csv`.

For reliable daily automation, add repository secrets `ALPACA_API_KEY_ID` and
`ALPACA_API_SECRET_KEY`. The optional repository variable `ALPACA_FEED` may be
`sip` (default) or `iex`. Without Alpaca credentials the scanner attempts a
Yahoo Finance fallback, but refuses to publish if data coverage is below 85%.

```bash
python volatility_compression_scanner.py \
  --symbols data/us_1b_universe.txt \
  --provider auto
```
