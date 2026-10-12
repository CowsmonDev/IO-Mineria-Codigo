"""Individual DBSCAN run and fixed cases with their outputs."""

from pathlib import Path

import pandas as pd

from src.data.constants import Columns
from src.data.schemas import ClusteringInput
from src.methods import dbscan
from src.methods.schemas import ClusteringResult
from src.runs._reporting import print_result
from src.runs.schemas import ClusteringRun
from src.runs.visualization.outputs import (
    generate_dbscan_experiment_plots,
    generate_method_plots,
)

EPS = dbscan.EPS
MIN_SAMPLES = dbscan.MIN_SAMPLES

# Representative cases from the exploration; this is not parameter selection.
CASE_CONFIGURATIONS = (
    ("reference", "Original configuration", 1.5, 5),
    ("seven_low_noise", "Seven groups with little noise", 1.175, 4),
    ("seven_more_noise", "Seven groups with more noise", 0.5, 10),
    ("fourteen_groups", "More groups", 0.5, 6),
    ("fragmentation", "Small radius and high fragmentation", 0.18, 5),
)


def run_cases(
    entry: ClusteringInput,
    directory: str | Path,
    *,
    eps: float = EPS,
    min_samples: int = MIN_SAMPLES,
) -> ClusteringRun[ClusteringResult]:
    """Run the requested settings and the five documented cases.

    Case names describe observations on the reference date; they do not guarantee
    the same number of groups when the data or analysis date changes."""
    matrix, original_values = entry["matrix"], entry["original_values"]
    result = dbscan.analyze(matrix, original_values, eps=eps, min_samples=min_samples)
    cases = [
        {
            "name": name,
            "description": description,
            "result": (
                result
                if (eps, min_samples) == (radius, minimum)
                else dbscan.analyze(
                    matrix, original_values, eps=radius, min_samples=minimum
                )
            ),
        }
        for name, description, radius, minimum in CASE_CONFIGURATIONS
    ]
    directory = Path(directory)
    generate_method_plots(entry, {"dbscan": result}, directory)
    generate_dbscan_experiment_plots(entry, cases, directory)
    print_result("dbscan", result)
    rows = []
    for case in cases:
        r = case["result"]
        sizes = r["summary"].drop(index=-1, errors="ignore")[Columns.COUNT]
        rows.append(
            {
                "caso": case["name"],
                **r["parameters"],
                "n_groups": r["n_groups"],
                "ruido_pct": 100 * r["noise"] / len(matrix),
                "mayor_pct_agrupados": (
                    100 * sizes.max() / sizes.sum() if len(sizes) else float("nan")
                ),
                "silhouette_sin_ruido": r["silhouette_mean"],
                "evaluados_silhouette": r["silhouette_population"],
            }
        )
        print_result(f"DBSCAN — {case['description']}", r)
    print("\nDBSCAN — fixed case comparison (largest group excludes noise):")
    print(pd.DataFrame(rows).to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    return {"result": result, "cases": cases}
