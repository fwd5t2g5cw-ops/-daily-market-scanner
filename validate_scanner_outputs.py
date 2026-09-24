from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_SCHEMAS = {
    'blue_marker_today': {'symbol', 'marker', 'blue_marker'},
    'double_reclaim_all': {'symbol', 'status', 'grade', 'quality_score'},
    'double_reclaim_ready_now': {'symbol', 'status', 'grade', 'quality_score'},
    'double_reclaim_today': {'symbol', 'double_reclaim'},
    'double_reclaim_top30': {'symbol', 'status', 'grade', 'quality_score'},
    'entry_marker_today': {'symbol', 'entry_marker'},
    'high_conviction_entry_today': {'symbol', 'high_conviction_entry'},
    'pine_entry_today': {'symbol', 'marker', 'blue_marker'},
    'pre_breakout_compression_today': {'symbol', 'compression_setup'},
    'pre_entry_watch_today': {'symbol', 'setup'},
    'reclaim_breakout_only_today': {'symbol', 'reclaim_breakout_only'},
    'reclaim_breakout_today': {'symbol', 'reclaim_breakout'},
    'signals_with_candles': {'symbol', 'entry_marker', 'double_reclaim', 'reclaim_breakout'},
}


def validate_outputs(market: str, outdir: Path) -> None:
    errors: list[str] = []
    for suffix, required in EXPECTED_SCHEMAS.items():
        path = outdir / f'{market}_{suffix}.csv'
        if not path.is_file():
            errors.append(f'missing {path}')
            continue
        with path.open(newline='', encoding='utf-8-sig') as handle:
            header = next(csv.reader(handle), None)
        if not header or not any(field.strip() for field in header):
            errors.append(f'{path} has no CSV header')
            continue
        missing = sorted(required.difference(header))
        if missing:
            errors.append(f'{path} is missing columns: {", ".join(missing)}')

    if errors:
        raise ValueError('Scanner output validation failed:\n- ' + '\n- '.join(errors))

    print(f'Validated {len(EXPECTED_SCHEMAS)} {market.upper()} scanner output files in {outdir}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--market', choices=['us', 'hk', 'canada'], required=True)
    parser.add_argument('--outdir', type=Path)
    args = parser.parse_args()
    outdir = args.outdir or Path('double_reclaim_results') / args.market
    validate_outputs(args.market, outdir)


if __name__ == '__main__':
    main()
