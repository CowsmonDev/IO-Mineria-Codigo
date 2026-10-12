"""Parameterization and experiments retaining features and identities."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from numpy.typing import ArrayLike, NDArray
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import adjusted_rand_score

from src.data.constants import Columns
from src.data.schemas import ClusteringInput
from src.methods import kmeans
from src.runs.kmeans_experiments import compare_profiles, explore


def test_parameters_and_cached_distances_preserve_fit(
    entry: ClusteringInput,
) -> None:
    matrix = entry["matrix"].copy()
    original_values = entry["original_values"].copy()
    distances = squareform(pdist(matrix))
    for k in (2, 5, 7):
        directo = kmeans.analyze(
            matrix, original_values, n_clusters=k, n_init=3, random_state=8
        )
        cacheado = kmeans.analyze(
            matrix,
            original_values,
            n_clusters=k,
            n_init=3,
            random_state=8,
            silhouette_distances=distances,
        )
        assert len(np.unique(directo["labels"])) == k
        np.testing.assert_array_equal(directo["labels"], cacheado["labels"])
        np.testing.assert_allclose(directo["silhouette"], cacheado["silhouette"])
        assert directo["parameters"]["n_init"] == 3
        assert directo["parameters"]["random_state"] == 8
    pd.testing.assert_frame_equal(entry["matrix"], matrix)
    pd.testing.assert_frame_equal(entry["original_values"], original_values)
    assert kmeans.PARAMETERS["n_clusters"] == 7
    assert kmeans.PARAMETERS["n_init"] == 25


@pytest.mark.parametrize("k", [1, 70, 71])
def test_rejects_k_without_valid_silhouette(entry: ClusteringInput, k: int) -> None:
    with pytest.raises(ValueError, match="n_clusters"):
        kmeans.analyze(entry["matrix"], entry["original_values"], n_clusters=k)


def test_rejects_misaligned_original_values(entry: ClusteringInput) -> None:
    with pytest.raises(ValueError, match="length"):
        kmeans.analyze(entry["matrix"], entry["original_values"].iloc[:-1])


def test_exploration_exports_assignments_and_preserves_attributes(
    entry: ClusteringInput,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def synthetic_reference(
        matrix: ArrayLike,
        original_values: pd.DataFrame,
    ) -> dict[str, NDArray[np.int64]]:
        return {"labels": np.repeat(np.arange(1, 8, dtype=np.int64), 10)}

    monkeypatch.setattr(
        "src.runs.kmeans_experiments.hierarchical.analyze", synthetic_reference
    )
    matrix, original_values = entry["matrix"].copy(), entry["original_values"].copy()
    result = explore(
        entry,
        tmp_path,
        k_values=(2, 3),
        seeds=(123, 0),
        n_init=2,
        n_init_control=3,
        control_threshold=0,
    )
    assert len(result["metrics"]) == 4
    assert len(result["seed_pairs"]) == 2
    pd.testing.assert_frame_equal(matrix, entry["matrix"])
    pd.testing.assert_frame_equal(original_values, entry["original_values"])
    protocol = json.loads((tmp_path / "protocol.json").read_text())
    assert protocol["features"] == list(original_values.columns)
    assert Columns.DROPPED_OUT in protocol["features"]
    assert protocol["state"] == "complete"
    assignments = pd.read_csv(tmp_path / "all_assignments.csv")
    np.testing.assert_array_equal(assignments[Columns.STUDENT_ID], entry["student_ids"])
    for case in result["representatives"]:
        folder = tmp_path / case["name"]
        cross_table = pd.read_csv(folder / "correspondence.csv", index_col=0)
        by_row = pd.read_csv(folder / "proportions_by_hierarchical.csv", index_col=0)
        by_column = pd.read_csv(folder / "proportions_by_kmeans.csv", index_col=0)
        assert cross_table.to_numpy().sum() == len(original_values)
        np.testing.assert_allclose(by_row.sum(axis=1), 1)
        np.testing.assert_allclose(by_column.sum(axis=0), 1)
        assert Columns.DROPPED_OUT in pd.read_csv(folder / "means.csv").columns
        assert (folder / "plots/correspondence.png").is_file()
        r = case["result"]
        metric = result["metrics"]
        metric = metric.loc[
            (metric["k"] == r["parameters"]["n_clusters"])
            & (metric["seed"] == r["parameters"]["random_state"])
        ].iloc[0]
        assert metric["ari_hierarchical"] == pytest.approx(
            adjusted_rand_score(assignments["jerarquico"], r["labels"])
        )
        persistence = pd.read_csv(folder / "profile_persistence.csv")
        assert len(persistence) == 2 * r["parameters"]["n_clusters"]
    assert (tmp_path / "reference/plots/correspondence.png").is_file()


def test_exploration_rejects_single_seed(
    entry: ClusteringInput, tmp_path: Path
) -> None:
    with pytest.raises(ValueError, match="two distinct seeds"):
        explore(entry, tmp_path, seeds=(123,))


def test_persistence_ignores_label_numbers_and_detects_changes() -> None:
    reference = np.array([1, 1, 1, 2, 2, 2], dtype=np.int64)
    permuted = np.array([9, 9, 9, 4, 4, 4], dtype=np.int64)
    table = compare_profiles(reference, permuted)
    np.testing.assert_array_equal(table["grupo_semilla"], [9, 4])
    np.testing.assert_allclose(table["jaccard"], 1)
    changed = np.array([9, 9, 4, 4, 4, 4], dtype=np.int64)
    table = compare_profiles(reference, changed)
    np.testing.assert_allclose(table["jaccard"], [2 / 3, 3 / 4])
    np.testing.assert_allclose(table["retencion"], [2 / 3, 1])
