from __future__ import annotations

import tempfile
import unittest
from io import StringIO
from pathlib import Path

import pandas as pd

from hk_double_reclaim_scanner import HK_OUTPUT_COLUMNS, _result_frame
from merge_signal_candles import DERIVED_SIGNAL_COLUMNS, prepare_empty_signal_output
from pine_entry_scanner import ENTRY_COLUMNS, _entry_output_frame
from pre_entry_scanner import PRE_ENTRY_COLUMNS, _pre_entry_output_frame
from validate_scanner_outputs import EXPECTED_SCHEMAS, validate_outputs


class EmptyOutputSchemaTests(unittest.TestCase):
    def assert_csv_round_trip(self, frame: pd.DataFrame) -> None:
        buffer = StringIO()
        frame.to_csv(buffer, index=False)
        parsed = pd.read_csv(StringIO(buffer.getvalue()))
        self.assertEqual(list(parsed.columns), list(frame.columns))
        self.assertTrue(parsed.empty)

    def test_empty_pine_entry_has_header(self) -> None:
        frame = _entry_output_frame([], 'market_cap_hkd')
        self.assertEqual(list(frame.columns), [*ENTRY_COLUMNS, 'market_cap_hkd'])
        self.assert_csv_round_trip(frame)

    def test_empty_pre_entry_has_header(self) -> None:
        frame = _pre_entry_output_frame([])
        self.assertEqual(list(frame.columns), PRE_ENTRY_COLUMNS)
        self.assert_csv_round_trip(frame)

    def test_empty_hk_double_reclaim_has_header(self) -> None:
        frame = _result_frame([])
        self.assertEqual(list(frame.columns), HK_OUTPUT_COLUMNS)
        self.assert_csv_round_trip(frame)

    def test_empty_unified_output_has_derived_columns(self) -> None:
        frame = prepare_empty_signal_output(pd.DataFrame(columns=HK_OUTPUT_COLUMNS))
        self.assertTrue(set(DERIVED_SIGNAL_COLUMNS).issubset(frame.columns))
        self.assert_csv_round_trip(frame)


class OutputValidationTests(unittest.TestCase):
    def test_header_only_result_set_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outdir = Path(directory)
            for suffix, required in EXPECTED_SCHEMAS.items():
                pd.DataFrame(columns=sorted(required)).to_csv(
                    outdir / f'hk_{suffix}.csv', index=False
                )
            validate_outputs('hk', outdir)

    def test_headerless_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outdir = Path(directory)
            for suffix, required in EXPECTED_SCHEMAS.items():
                pd.DataFrame(columns=sorted(required)).to_csv(
                    outdir / f'hk_{suffix}.csv', index=False
                )
            (outdir / 'hk_blue_marker_today.csv').write_text('\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'has no CSV header'):
                validate_outputs('hk', outdir)


if __name__ == '__main__':
    unittest.main()
