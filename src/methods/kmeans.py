"""Configurable K-Means with the original protocol as the default."""

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples

from src.data.constants import Columns
from src.methods.schemas import KMeansParameters, KMeansResult

PARAMETERS: KMeansParameters = {
    "n_clusters": 7,
    "init": "k-means++",
    "n_init": 25,
    "random_state": 123,
    "algorithm": "lloyd",
    "max_iter": 300,
    "tol": 1e-4,
}


def analyze(
    matrix: ArrayLike,
    original_values: pd.DataFrame,
    *,
    n_clusters: int = 7,
    n_init: int = 25,
    random_state: int = 123,
    silhouette_distances: ArrayLike | None = None,
) -> KMeansResult:
    """Cluster unchanged features and rows, and summarize in original units.

    Optional precomputed Euclidean distances can be reused across experiments.
    They must match the input matrix and its row order."""
    x = np.asarray(matrix, dtype=float)
    if x.ndim != 2 or x.shape[1] == 0 or not np.isfinite(x).all():
        raise ValueError("The matrix must have two dimensions and finite values.")
    if len(original_values) != len(x):
        raise ValueError("Original values and the matrix must have the same length.")
    if not isinstance(n_clusters, int) or isinstance(n_clusters, bool):
        raise TypeError("n_clusters must be an integer.")
    if not 2 <= n_clusters < len(x):
        raise ValueError("Require 2 <= n_clusters < number of observations.")
    if len(np.unique(x, axis=0)) < n_clusters:
        raise ValueError("Not enough distinct observations for the requested groups.")
    if not isinstance(n_init, int) or isinstance(n_init, bool) or n_init < 1:
        raise ValueError("n_init must be a positive integer.")
    parameters: KMeansParameters = {
        **PARAMETERS,
        "n_clusters": n_clusters,
        "n_init": n_init,
        "random_state": random_state,
    }
    model = KMeans(**parameters).fit(x)
    labels = (model.labels_ + 1).astype(np.int64)
    if silhouette_distances is None:
        silhouette = silhouette_samples(x, labels)
    else:
        distances = np.asarray(silhouette_distances, dtype=float)
        if distances.shape != (len(x), len(x)):
            raise ValueError("Distances must correspond to all input rows.")
        silhouette = silhouette_samples(distances, labels, metric="precomputed")
    grouped = (
        original_values.reset_index(drop=True)
        .assign(**{Columns.GROUP: labels})
        .groupby(Columns.GROUP)
    )
    summary = grouped.mean()
    summary.insert(0, Columns.COUNT, grouped.size())
    return {
        "labels": labels,
        "summary": summary,
        "silhouette": silhouette,
        "silhouette_mean": float(silhouette.mean()),
        "silhouette_population": len(x),
        "silhouette_reason": "",
        "inertia": float(model.inertia_),
        "centers": model.cluster_centers_,
        "iterations": int(model.n_iter_),
        "parameters": parameters,
    }
