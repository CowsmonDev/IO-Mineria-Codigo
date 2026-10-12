"""Command-line entry point for the clustering comparison."""

import argparse
from pathlib import Path

from src.runs import dbscan
from src.runs.comparison import REFERENCE_DATE, main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--date",
        dest="date",
        help=f"Analysis date; defaults to ANALYSIS_DATE or {REFERENCE_DATE}.",
    )
    parser.add_argument(
        "--output",
        dest="output",
        type=Path,
        help="Output root; contains <method>/plots/.",
    )
    parser.add_argument(
        "--eps", type=float, default=dbscan.EPS, help="DBSCAN radius (default: 1.5)."
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=dbscan.MIN_SAMPLES,
        help="Minimum DBSCAN neighborhood size, including self (default: 5).",
    )
    args = parser.parse_args()
    main(date=args.date, output=args.output, eps=args.eps, min_samples=args.min_samples)
