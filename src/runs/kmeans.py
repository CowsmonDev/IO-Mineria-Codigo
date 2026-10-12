"""Run K-Means and generate its outputs."""

from pathlib import Path

from src.data.schemas import ClusteringInput
from src.methods import kmeans
from src.methods.schemas import KMeansResult
from src.runs._reporting import print_result
from src.runs.schemas import ClusteringRun
from src.runs.visualization.outputs import generate_method_plots


def run_cases(
    entry: ClusteringInput, directory: str | Path
) -> ClusteringRun[KMeansResult]:
    """Run the reference configuration; the separate experiment runner explores k."""
    result = kmeans.analyze(entry["matrix"], entry["original_values"])
    generate_method_plots(entry, {"kmeans": result}, Path(directory))
    print_result("kmeans", result)
    return {
        "result": result,
        "cases": [
            {
                "name": "reference",
                "description": "K-Means k=7",
                "result": result,
            }
        ],
    }
