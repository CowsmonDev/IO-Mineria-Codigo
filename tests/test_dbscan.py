"""Explicit DBSCAN settings, noise and valid Silhouette calculations."""

import numpy as np
import pandas as pd
import pytest
from numpy.typing import NDArray
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors

from src.data.constants import Columns
from src.methods.dbscan import analyze


@pytest.fixture
def matrix() -> NDArray[np.float64]:
    rng = np.random.default_rng(8)
    return np.vstack(
        [rng.normal(-2, 0.03, (25, 2)), rng.normal(2, 0.03, (25, 2)), [[20, 20]]]
    )


def test_preserves_noise_and_excludes_it_only_from_silhouette(
    matrix: NDArray[np.float64],
) -> None:
    original_values = pd.DataFrame(matrix, columns=["a", "b"])
    result = analyze(matrix, original_values, eps=0.2, min_samples=5)
    esperado = DBSCAN(eps=0.2, min_samples=5).fit(matrix)
    np.testing.assert_array_equal(
        result["labels"],
        np.where(esperado.labels_ == -1, -1, esperado.labels_ + 1),
    )
    assert result["noise"] == 1 and result["n_groups"] == 2
    assert result["silhouette_population"] == 50
    assert np.isnan(result["silhouette"][-1])
    assert result["silhouette_mean"] == pytest.approx(
        silhouette_score(matrix[:-1], result["labels"][:-1])
    )
    assert result["summary"].loc[-1, Columns.COUNT] == 1
    assert result["summary"][Columns.COUNT].sum() == len(matrix)


def test_neighbors_include_self(matrix: NDArray[np.float64]) -> None:
    result = analyze(matrix, pd.DataFrame(matrix))
    esperadas = NearestNeighbors(n_neighbors=5).fit(matrix).kneighbors(matrix)[0][:, 4]
    np.testing.assert_allclose(result["neighbor_distances"], np.sort(esperadas))


@pytest.mark.parametrize("eps", [1e-12, 100])
def test_all_noise_or_single_group_does_not_interrupt_analysis(
    matrix: NDArray[np.float64], eps: float
) -> None:
    result = analyze(matrix, pd.DataFrame(matrix), eps=eps, min_samples=5)
    assert np.isnan(result["silhouette_mean"])
    assert result["silhouette_reason"]
    assert result["silhouette_population"] == 0
    assert result["n_groups"] == (0 if eps == 1e-12 else 1)


@pytest.mark.parametrize(
    "eps, min_samples", [(0, 5), (float("nan"), 5), (1.5, 1), (1.5, 100)]
)
def test_rejects_invalid_parameters(
    matrix: NDArray[np.float64], eps: float, min_samples: int
) -> None:
    with pytest.raises(ValueError, match="Require"):
        analyze(matrix, pd.DataFrame(matrix), eps=eps, min_samples=min_samples)
