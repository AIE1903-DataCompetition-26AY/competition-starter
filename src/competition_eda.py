"""Training-only graphics for the AIE1903 wireless traffic competition.

Use your authorized copy of train.csv. This package does not contain the
competition CSV files or any test ground truth. Timestamps are left in their
recorded clock because the description does not specify a time zone.

Example:
    python competition_eda.py --data-dir ../course-data --cell Cell_177
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

CELL_COLUMNS = [f'Cell_{i:03d}' for i in range(1, 218)]
COLUMNS = ['timestamp', *CELL_COLUMNS]
START = pd.Timestamp('2024-11-30 23:00:00')


def load_train(path: Path) -> pd.DataFrame:
    """Validate the released training schema and preserve its recorded clock."""
    if not path.is_file():
        raise FileNotFoundError(
            f'{path} not found. Download the authorized course data first; '
            'then set --data-dir to its folder.')
    frame = pd.read_csv(path, parse_dates=['timestamp'])
    if frame.columns.tolist() != COLUMNS:
        raise ValueError('Expected timestamp followed by Cell_001 ... Cell_217, in that order.')
    expected = pd.date_range(START, periods=1728, freq='5min')
    observed = pd.DatetimeIndex(frame['timestamp'])
    if not observed.equals(expected):
        raise ValueError('Training timestamps must match the 1,728-point chronological grid.')
    try:
        values = frame[CELL_COLUMNS].to_numpy(dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError('Training traffic columns must be numeric.') from exc
    if not np.isfinite(values).all() or (values < 1).any():
        raise ValueError('The description specifies finite training counts of at least 1.')
    if not np.equal(values, np.floor(values)).all():
        raise ValueError('The released traffic values are integer-valued counts.')
    return frame


def validate_test(path: Path) -> None:
    """Validate timestamp-only test inputs; blank target cells are intentional."""
    if not path.is_file():
        return
    frame = pd.read_csv(path, parse_dates=['timestamp'])
    if frame.columns.tolist() != COLUMNS:
        raise ValueError('test.csv has an unexpected column schema.')
    expected = pd.date_range('2024-12-06 23:00:00', periods=289, freq='5min')
    if not pd.DatetimeIndex(frame['timestamp']).equals(expected):
        raise ValueError('Expected exactly 289 test timestamps on the prescribed grid.')
    if not frame[CELL_COLUMNS].isna().all().all():
        raise ValueError('Released test.csv should not contain any traffic ground truth.')


def full_calendar_days(train: pd.DataFrame, cell: str) -> pd.DataFrame:
    """Exclude partial boundary dates, rather than filling or averaging them."""
    if cell not in CELL_COLUMNS:
        raise ValueError(f'Unknown cell: {cell}')
    frame = train[['timestamp', cell]].copy()
    frame['Day'] = frame['timestamp'].dt.date
    frame['Slot'] = (frame['timestamp'].dt.hour * 12
                     + frame['timestamp'].dt.minute // 5)
    size = frame.groupby('Day')['Slot'].transform('nunique')
    return frame.loc[size.eq(288)].sort_values(['Day', 'Slot'])


def create_plots(train: pd.DataFrame, cell: str, output: Path) -> list[Path]:
    if cell not in CELL_COLUMNS:
        raise ValueError(f'Unknown cell: {cell}')
    output.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    fig = plt.figure(figsize=(10, 4), layout='constrained')
    ax = fig.gca()
    ax.plot(train['timestamp'], train[cell], linewidth=1)
    ax.set(title=f'{cell}: released training history', xlabel='Recorded timestamp',
           ylabel='Uplink count per 5-minute window')
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{x / 1e6:g}M'))
    ax.grid(True, alpha=0.2)
    for ext in ('png', 'pdf'):
        path = output / f'{cell}_time.{ext}'
        fig.savefig(path, dpi=250, bbox_inches='tight')
        paths.append(path)
    plt.close(fig)

    daily = full_calendar_days(train, cell)
    fig = plt.figure(figsize=(10, 4), layout='constrained')
    ax = fig.gca()
    for day, part in daily.groupby('Day', sort=True):
        ax.plot(part['Slot'] / 12, part[cell], linewidth=1, label=str(day))
    ax.set(title=f'{cell}: complete calendar days only', xlabel='Recorded hour of day',
           ylabel='Uplink count per 5-minute window', xlim=(0, 24))
    ax.set_xticks(range(0, 25, 4))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{x / 1e6:g}M'))
    ax.grid(True, alpha=0.2)
    ax.legend(fontsize=8, ncol=3)
    for ext in ('png', 'pdf'):
        path = output / f'{cell}_daily_overlay.{ext}'
        fig.savefig(path, dpi=250, bbox_inches='tight')
        paths.append(path)
    plt.close(fig)
    print(f'{cell}: {len(train)} training rows, {daily.Day.nunique()} complete calendar days.')
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path('../course-data'))
    parser.add_argument('--cell', default='Cell_177', choices=CELL_COLUMNS)
    parser.add_argument('--output-dir', type=Path, default=Path('output/competition'))
    args = parser.parse_args()
    train = load_train(args.data_dir / 'train.csv')
    validate_test(args.data_dir / 'test.csv')
    for path in create_plots(train, args.cell, args.output_dir):
        print(path)


if __name__ == '__main__':
    main()
