"""Common input and preservation of the K-Means protocol."""

import numpy as np
import pytest
from sklearn.metrics import adjusted_rand_score

from src.data.constants import Columns
from src.data.preparation import validate_input
from src.data.schemas import ClusteringInput
from src.methods.kmeans import analyze


def test_rejects_reordered_rows(entry: ClusteringInput) -> None:
    entry["matrix"] = entry["matrix"].iloc[::-1]
    with pytest.raises(ValueError, match="order"):
        validate_input(entry)


def test_rejects_labels_as_features(entry: ClusteringInput) -> None:
    entry["matrix"]["cluster"] = 1
    with pytest.raises(ValueError, match="labels"):
        validate_input(entry)


def test_rejects_duplicate_identifiers(entry: ClusteringInput) -> None:
    entry["student_ids"][1] = entry["student_ids"][0]
    with pytest.raises(ValueError, match="unique"):
        validate_input(entry)


def test_kmeans_separates_profiles_without_mutating_input(
    entry: ClusteringInput,
) -> None:
    matrix = entry["matrix"].to_numpy(copy=True)
    result = analyze(matrix, entry["original_values"])
    np.testing.assert_array_equal(matrix, entry["matrix"].to_numpy())
    assert len(np.unique(result["labels"])) == 7
    assert adjusted_rand_score(np.repeat(range(7), 10), result["labels"]) == 1
    assert result["parameters"]["random_state"] == 123
    assert result["summary"][Columns.COUNT].sum() == len(matrix)
    assert result["silhouette_population"] == len(matrix)
