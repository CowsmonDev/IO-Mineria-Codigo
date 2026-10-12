"""Method result contracts for typing, without runtime validation."""

from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict

import numpy as np
import pandas as pd
from numpy.typing import NDArray

if TYPE_CHECKING:
    from glmnet import LogitNet


class KMeansParameters(TypedDict):
    """Explicit settings for a K-Means fit."""

    n_clusters: int
    init: Literal["k-means++"]
    n_init: int
    random_state: int
    algorithm: Literal["lloyd"]
    max_iter: int
    tol: float


class KMeansResult(TypedDict):
    """Per-row assignments and fit diagnostics for the common input."""

    labels: NDArray[np.int64]
    summary: pd.DataFrame
    silhouette: NDArray[np.float64]
    silhouette_mean: float
    silhouette_population: int
    silhouette_reason: str
    inertia: float
    centers: NDArray[np.float64]
    iterations: int
    parameters: KMeansParameters


class ClusteringParameters(TypedDict, total=False):
    """Hierarchical and DBSCAN method settings."""

    metric: str
    method: str
    height: float
    eps: float
    min_samples: int


class ClusteringResult(TypedDict):
    """Common result with optional method-specific diagnostics."""

    labels: NDArray[np.int64]
    summary: pd.DataFrame
    silhouette: NDArray[np.float64]
    silhouette_mean: float
    silhouette_population: int
    silhouette_reason: str
    parameters: ClusteringParameters
    linkage_matrix: NotRequired[NDArray[np.float64]]
    silhouette_by_k: NotRequired[pd.Series]
    noise: NotRequired[int]
    n_groups: NotRequired[int]
    neighbor_distances: NotRequired[NDArray[np.float64]]


class LassoResult(TypedDict):
    """Model and original coefficients of the supervised baseline."""

    model: "LogitNet"
    coefficients: pd.Series
