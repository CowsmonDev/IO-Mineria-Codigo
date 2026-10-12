"""Fixed reference: Euclidean distance, Ward linkage and height 35."""

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from scipy.cluster.hierarchy import cut_tree, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import silhouette_samples, silhouette_score

from src.data.constants import Columns
from src.methods.schemas import ClusteringResult


def analyze(matrix: ArrayLike, original_values: pd.DataFrame) -> ClusteringResult:
    """Return reference labels, Silhouette values and group means."""
    x = np.asarray(matrix, dtype=float)
    distances = pdist(x, metric="euclidean")
    linkage_matrix = linkage(distances, method="ward")
    labels = cut_tree(linkage_matrix, height=35).reshape(-1) + 1
    if len(np.unique(labels)) != 7:
        raise ValueError(
            "The cut at height 35 does not reproduce the seven reference groups."
        )
    square_distances = squareform(distances)
    silhouette = silhouette_samples(square_distances, labels, metric="precomputed")
    # Original R diagnostic; retains the fixed cut at height 35.
    silhouette_by_k = pd.Series(
        {
            k: silhouette_score(
                square_distances,
                cut_tree(linkage_matrix, n_clusters=k).reshape(-1),
                metric="precomputed",
            )
            for k in range(2, min(16, len(x)))
        },
        name="silhouette",
    )
    silhouette_by_k.index.name = "k"
    grouped = (
        original_values.reset_index(drop=True)
        .assign(**{Columns.GROUP: labels})
        .groupby(Columns.GROUP)
    )
    summary = grouped.mean()
    summary.insert(0, Columns.COUNT, grouped.size())
    return {
        "labels": labels,
        "linkage_matrix": linkage_matrix,
        "summary": summary,
        "silhouette": silhouette,
        "silhouette_mean": float(silhouette.mean()),
        "silhouette_by_k": silhouette_by_k,
        "silhouette_population": len(x),
        "silhouette_reason": "",
        "parameters": {"metric": "euclidean", "method": "ward", "height": 35},
    }
