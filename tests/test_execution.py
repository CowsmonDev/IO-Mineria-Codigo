"""The main run preserves input data and hierarchical reference outputs."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from numpy.typing import NDArray
from scipy.cluster.hierarchy import linkage
from sklearn.metrics import silhouette_samples

from main import main
from src.data.constants import Columns
from src.data.schemas import ClusteringInput
from src.methods import hierarchical
from src.methods.schemas import ClusteringResult
from src.runs import dbscan as run_dbscan


def test_run_generates_plots_when_dbscan_has_no_silhouette(
    entry: ClusteringInput, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def synthetic_reference(
        matrix: NDArray[np.float64], original_values: pd.DataFrame
    ) -> ClusteringResult:
        # The h=35 cut is fixed for the real population, not this small sample.
        groups = np.repeat(np.arange(1, 8), 10)
        grouped = original_values.assign(**{Columns.GROUP: groups}).groupby(
            Columns.GROUP
        )
        summary = grouped.mean()
        summary.insert(0, Columns.COUNT, grouped.size())
        values = silhouette_samples(matrix, groups)
        return {
            "labels": groups,
            "linkage_matrix": linkage(matrix, method="ward"),
            "summary": summary,
            "silhouette": values,
            "silhouette_mean": values.mean(),
            "silhouette_by_k": pd.Series([0.1, 0.2], index=[2, 3]),
            "silhouette_population": len(matrix),
            "silhouette_reason": "",
            "parameters": {"height": 35},
        }

    monkeypatch.setattr(hierarchical, "analyze", synthetic_reference)

    def prepare_synthetic_input(*, analysis_date: str) -> ClusteringInput:
        assert analysis_date == "2026-10-01"
        return entry

    monkeypatch.setattr("src.runs.comparison.prepare_input", prepare_synthetic_input)
    original, matrix = entry["original_values"].copy(), entry["matrix"].copy()
    result = main(date="2026-10-01", output=tmp_path, eps=100, min_samples=5)
    pd.testing.assert_frame_equal(entry["original_values"], original)
    pd.testing.assert_frame_equal(entry["matrix"], matrix)
    np.testing.assert_array_equal(result["entry"]["student_ids"], entry["student_ids"])
    assert set(result["results"]) == {"hierarchical", "kmeans", "dbscan"}
    assert result["results"]["dbscan"]["n_groups"] == 1
    cases = result["dbscan_cases"]
    assert [case["name"] for case in cases] == [
        config[0] for config in run_dbscan.CASE_CONFIGURATIONS
    ]
    for case, (_, _, eps, minimum) in zip(cases, run_dbscan.CASE_CONFIGURATIONS):
        r = case["result"]
        assert r["parameters"]["eps"] == eps
        assert r["parameters"]["min_samples"] == minimum
        assert len(r["labels"]) == len(original)
        assert r["summary"][Columns.COUNT].sum() == len(original)
        folder = tmp_path / "dbscan/experiments" / case["name"] / "plots"
        for name in ("sizes", "silhouette", "neighbors", "dropout_profile"):
            assert (folder / f"{name}.png").is_file()
    assert (tmp_path / "dbscan/experiments/plots/comparison.png").is_file()
    for method in ("hierarchical", "dbscan", "k-means"):
        assert (tmp_path / method / "plots/silhouette.png").is_file()
        assert (tmp_path / method / "plots/sizes.png").is_file()
    assert (tmp_path / "dbscan/plots/neighbors.png").is_file()
    assert (tmp_path / "hierarchical/plots/overall_dendrogram.png").is_file()
    assert not list(tmp_path.glob("*.png"))
    summary = tmp_path / "hierarchical/cluster_summary.csv"
    assert pd.read_csv(summary)["cantidad_observaciones"].sum() == len(original)
    assert list(tmp_path.rglob("*.csv")) == [summary]
    assert (tmp_path / "hierarchical/plots/cluster_dendrogram_1.pdf").is_file()
    assert (tmp_path / "hierarchical/plots/silhouette_by_k.png").is_file()
    assert not list(tmp_path.rglob("*.json"))


def test_kmeans_and_dbscan_runs_generate_outputs_independently(
    entry: ClusteringInput, tmp_path: Path
) -> None:
    from src.runs import kmeans as run_kmeans

    kmeans_run = run_kmeans.run_cases(entry, tmp_path)
    dbscan_run = run_dbscan.run_cases(entry, tmp_path)

    assert set(kmeans_run) == set(dbscan_run) == {"result", "cases"}
    assert len(kmeans_run["cases"]) == 1
    assert len(dbscan_run["cases"]) == 5
    # The default configuration matches the first case and reuses its fit.
    assert dbscan_run["result"] is dbscan_run["cases"][0]["result"]
    assert (tmp_path / "k-means/plots/silhouette.png").is_file()
    assert (tmp_path / "dbscan/plots/neighbors.png").is_file()
    assert (tmp_path / "dbscan/experiments/plots/comparison.png").is_file()
    assert not (tmp_path / "hierarchical").exists()
