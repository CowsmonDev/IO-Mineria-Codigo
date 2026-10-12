"""Prepare the common input and coordinate method runs."""

import os
from pathlib import Path

import pandas as pd

from src.data.preparation import prepare_input, validate_input
from src.runs import dbscan, hierarchical, kmeans
from src.runs.schemas import ComparisonResult

ROOT = Path(__file__).resolve().parents[2]
REFERENCE_DATE = "2026-10-01"


def main(
    *,
    date: str | pd.Timestamp | None = None,
    output: str | Path | None = None,
    eps: float = dbscan.EPS,
    min_samples: int = dbscan.MIN_SAMPLES,
) -> ComparisonResult:
    """Delegate methods and outputs to their runs using the same input."""
    date = (
        pd.Timestamp(date or os.environ.get("ANALYSIS_DATE") or REFERENCE_DATE)
        .date()
        .isoformat()
    )
    output = Path(output) if output is not None else ROOT / "output"
    print(f"Stage 1/4: common preparation (date {date})", flush=True)
    entry = prepare_input(analysis_date=date)
    validate_input(entry)

    print("Stage 2/4: hierarchical cases and outputs", flush=True)
    hierarchical_run = hierarchical.run_cases(entry, output)
    print("Stage 3/4: K-Means cases and outputs", flush=True)
    kmeans_run = kmeans.run_cases(entry, output)
    print(
        f"Stage 4/4: DBSCAN cases and outputs (eps={eps}, min_samples={min_samples})",
        flush=True,
    )
    dbscan_run = dbscan.run_cases(entry, output, eps=eps, min_samples=min_samples)
    print(f"\nPlots saved to: {output.resolve()}")
    return {
        "entry": entry,
        "results": {
            "hierarchical": hierarchical_run["result"],
            "kmeans": kmeans_run["result"],
            "dbscan": dbscan_run["result"],
        },
        "dbscan_cases": dbscan_run["cases"],
    }
