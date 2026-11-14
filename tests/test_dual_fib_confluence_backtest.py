import argparse

import pandas as pd

from dual_fib_confluence_backtest import evaluate_outcome, fib_price, normalize_ohlcv, relative_gap


def test_dec_geometry():
    # Approximate anchors reconstructed from the user's DEC chart.
    a_0382 = fib_price(14.99, 14.53385, 0.382)
    a_1618 = fib_price(14.99, 14.53385, 1.618)
    b_0382 = fib_price(12.658, 12.95653, 0.382)
    b_neg1618 = fib_price(12.658, 12.95653, -1.618)
    assert abs(a_0382 - 13.672) < 0.01
    assert abs(a_1618 - 16.31) < 0.02
    assert abs(b_0382 - 13.521) < 0.01
    assert abs(b_neg1618 - 16.31) < 0.02
    assert relative_gap(a_0382, b_0382) < 0.02
    assert relative_gap(a_1618, b_neg1618) < 0.02


def test_same_day_target_and_stop_is_failure():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=2),
            "open": [13.67, 13.50],
            "high": [16.50, 14.00],
            "low": [12.50, 13.00],
            "close": [14.00, 13.50],
        }
    )
    result = evaluate_outcome(df, 0, 13.67, 12.66, 16.31, 90)
    assert result["outcome"] == "FAIL_STOP"
    assert result["realized_r"] == -1.0


def test_target_before_stop_is_success():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3),
            "open": [13.67, 14.00, 16.00],
            "high": [14.20, 15.00, 16.40],
            "low": [13.40, 13.80, 15.70],
            "close": [14.00, 14.80, 16.20],
        }
    )
    result = evaluate_outcome(df, 0, 13.67, 12.66, 16.31, 90)
    assert result["outcome"] == "SUCCESS_TARGET"
    assert result["holding_days"] == 3


def test_yahoo_close_and_adjusted_close_do_not_collide():
    df = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=2),
            "Open": [10.0, 10.2],
            "High": [10.5, 10.6],
            "Low": [9.8, 10.0],
            "Close": [10.3, 10.4],
            "Adj Close": [10.1, 10.2],
            "Volume": [100, 120],
        }
    )
    result = normalize_ohlcv(df)
    assert result["close"].tolist() == [10.3, 10.4]
    assert result["adj_close"].tolist() == [10.1, 10.2]
