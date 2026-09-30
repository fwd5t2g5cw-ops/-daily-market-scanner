from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

from volatility_compression_scanner import (
    OUTPUT_COLUMNS,
    _alpaca_symbol,
    analyze_symbol,
    fetch_alpaca,
    result_frame,
    write_outputs,
)


def make_ohlcv(kind: str, periods: int = 420) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    index = pd.bdate_range("2024-01-02", periods=periods)
    if kind == "coil":
        returns = np.r_[
            rng.normal(0.0005, 0.025, periods - 35), rng.normal(0, 0.0012, 35)
        ]
    else:
        returns = rng.normal(0.0002, 0.025, periods)
    close = 100 * np.exp(np.cumsum(returns))
    spread = np.r_[
        rng.uniform(0.012, 0.04, periods - 35), rng.uniform(0.001, 0.003, 35)
    ]
    if kind != "coil":
        spread = rng.uniform(0.015, 0.045, periods)
    open_ = close * (1 + rng.normal(0, spread / 5))
    high = np.maximum(open_, close) * (1 + spread)
    low = np.minimum(open_, close) * (1 - spread)
    volume = rng.integers(800_000, 1_800_000, periods).astype(float)
    if kind == "coil":
        volume[-35:] *= 0.45
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    )


class CompressionModelTests(unittest.TestCase):
    def test_coil_scores_higher_than_loose(self) -> None:
        coil = analyze_symbol("COIL", make_ohlcv("coil"))
        loose = analyze_symbol("LOOSE", make_ohlcv("loose"))
        self.assertIsNotNone(coil)
        self.assertIsNotNone(loose)
        self.assertGreater(coil["score"], loose["score"])
        self.assertIn(coil["state"], {"COILED", "COMPRESSED"})

    def test_upside_expansion_requires_range_exit_and_true_range(self) -> None:
        frame = make_ohlcv("coil")
        prior_high = float(frame["high"].iloc[-11:-1].max())
        frame.iloc[-1, frame.columns.get_loc("close")] = prior_high * 1.04
        frame.iloc[-1, frame.columns.get_loc("open")] = prior_high * 0.98
        frame.iloc[-1, frame.columns.get_loc("high")] = prior_high * 1.06
        frame.iloc[-1, frame.columns.get_loc("low")] = prior_high * 0.96
        row = analyze_symbol("UP", frame)
        self.assertEqual(row["expansion_signal"], "UP_EXPANSION_CONFIRMED")

    def test_downside_detection_is_symmetric(self) -> None:
        frame = make_ohlcv("coil")
        prior_low = float(frame["low"].iloc[-11:-1].min())
        frame.iloc[-1, frame.columns.get_loc("close")] = prior_low * 0.96
        frame.iloc[-1, frame.columns.get_loc("open")] = prior_low * 1.02
        frame.iloc[-1, frame.columns.get_loc("high")] = prior_low * 1.04
        frame.iloc[-1, frame.columns.get_loc("low")] = prior_low * 0.94
        row = analyze_symbol("DOWN", frame)
        self.assertEqual(row["expansion_signal"], "DOWN_EXPANSION_CONFIRMED")

    def test_missing_volume_is_allowed(self) -> None:
        frame = make_ohlcv("coil").drop(columns="volume")
        row = analyze_symbol("NOVOL", frame)
        self.assertIsNotNone(row)
        self.assertFalse(row["volume_contraction"])

    def test_short_history_is_skipped(self) -> None:
        self.assertIsNone(analyze_symbol("SHORT", make_ohlcv("coil", 80)))

    def test_empty_output_has_stable_schema(self) -> None:
        self.assertEqual(list(result_frame([]).columns), OUTPUT_COLUMNS)

    def test_post_gap_coil_is_not_actionable(self) -> None:
        frame = make_ohlcv("coil")
        # Simulate the HZO pattern: a large event gap followed by a tight shelf.
        frame.iloc[-10:, :4] *= 1.5
        row = analyze_symbol("GAP", frame, benchmark=make_ohlcv("loose"))
        ranked = result_frame([row])
        self.assertFalse(bool(ranked.iloc[0]["prebreakout_eligible"]))
        self.assertIn("POST_GAP_COIL", ranked.iloc[0]["rejection_reasons"])

    def test_mature_strong_coil_can_be_actionable(self) -> None:
        row = analyze_symbol("READY", make_ohlcv("coil"), benchmark=make_ohlcv("loose"))
        row.update(
            {
                "state": "COILED",
                "expansion_signal": "NONE",
                "max_abs_gap_20d_pct": 1.0,
                "days_since_10pct_gap": 999,
                "return_20d_pct": 2.0,
                "sma50_distance_pct": 4.0,
                "distance_to_pivot_pct": -1.0,
                "close": 50.0,
                "avg_dollar_volume_20d": 20_000_000,
                "rs_63d_vs_spy_pct": 8.0,
            }
        )
        ranked = result_frame([row])
        self.assertTrue(bool(ranked.iloc[0]["prebreakout_eligible"]))
        self.assertEqual(ranked.iloc[0]["rejection_reasons"], "")

    def test_output_files_exist_even_when_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outdir = Path(directory)
            write_outputs(result_frame([]), ["A", "B"], set(), "test", outdir)
            self.assertEqual(
                list(pd.read_csv(outdir / "all.csv").columns), OUTPUT_COLUMNS
            )
            self.assertTrue((outdir / "summary.json").exists())
            self.assertEqual((outdir / "missing_symbols.txt").read_text(), "A\nB")
            self.assertTrue((outdir / "prebreakout_watch.csv").exists())
            self.assertTrue((outdir / "rejected_compression.csv").exists())


class AlpacaTests(unittest.TestCase):
    def test_class_share_symbol_mapping(self) -> None:
        self.assertEqual(_alpaca_symbol("BRK-B"), "BRK.B")

    @patch("volatility_compression_scanner.requests.get")
    def test_alpaca_pagination_and_reverse_mapping(self, get: Mock) -> None:
        first = Mock()
        first.raise_for_status.return_value = None
        first.json.return_value = {
            "bars": {
                "BRK.B": [
                    {
                        "t": "2025-01-02T05:00:00Z",
                        "o": 1,
                        "h": 2,
                        "l": 1,
                        "c": 2,
                        "v": 3,
                    }
                ]
            },
            "next_page_token": "next",
        }
        second = Mock()
        second.raise_for_status.return_value = None
        second.json.return_value = {
            "bars": {
                "BRK.B": [
                    {
                        "t": "2025-01-03T05:00:00Z",
                        "o": 2,
                        "h": 3,
                        "l": 2,
                        "c": 3,
                        "v": 4,
                    }
                ]
            },
            "next_page_token": None,
        }
        get.side_effect = [first, second]
        frames = fetch_alpaca(["BRK-B"], "key", "secret")
        self.assertEqual(len(frames["BRK-B"]), 2)
        self.assertEqual(get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
