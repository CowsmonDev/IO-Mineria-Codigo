"""DBSCAN with explicit parameters and neighbor-distance diagnostics."""

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_samples
from sklearn.neighbors import NearestNeighbors

from src.data.constants import Columns
from src.methods.schemas import ClusteringResult

EPS = 1.5
MIN_SAMPLES = 5


def analyze(
    matrix: ArrayLike,
    original_values: pd.DataFrame,
    *,
    eps: float = EPS,
    min_samples: int = MIN_SAMPLES,
) -> ClusteringResult:
    """Fit one configuration; exclude noise (-1) only from Silhouette."""
    x = np.asarray(matrix, dtype=float)
    if (
        not np.isfinite(eps)
        or eps <= 0
        or not isinstance(min_samples, int)
        or not 2 <= min_samples <= len(x)
    ):
        raise ValueError("Require positive finite eps and 2 <= min_samples <= n.")
    model = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean").fit(x)
    labels = np.where(model.labels_ == -1, -1, model.labels_ + 1)
    included = labels != -1
    n = int(included.sum())
    k = len(np.unique(labels[included]))
    silhouette = np.full(len(x), np.nan)
    reason = ""
    if 2 <= k < n:
        silhouette[included] = silhouette_samples(x[included], labels[included])
    else:
        reason = f"Silhouette unavailable: {k} groups and {n} non-noise students; require between 2 and n-1 groups."
    grouped = (
        original_values.reset_index(drop=True)
        .assign(**{Columns.GROUP: labels})
        .groupby(Columns.GROUP)
    )
    summary = grouped.mean()
    summary.insert(0, Columns.COUNT, grouped.size())
    # kneighbors(X) includes self; neighborhood size m uses column m-1.
    distances = (
        NearestNeighbors(n_neighbors=min_samples, metric="euclidean")
        .fit(x)
        .kneighbors(x)[0][:, min_samples - 1]
    )
    return {
        "labels": labels,
        "summary": summary,
        "silhouette": silhouette,
        "silhouette_mean": float(np.nanmean(silhouette)) if not reason else np.nan,
        "silhouette_population": n if not reason else 0,
        "silhouette_reason": reason,
        "noise": int((~included).sum()),
        "n_groups": k,
        "neighbor_distances": np.sort(distances),
        "parameters": {"eps": eps, "min_samples": min_samples, "metric": "euclidean"},
    }
