"""Fields consumed by plot builders from in-memory results.

These contracts describe the visualization subset; methods may return other
fields. They do not replace runtime data validation with Pandera."""

from typing import NotRequired, TypedDict

import numpy as np
import pandas as pd
from numpy.typing import NDArray


class PlotParameters(TypedDict, total=False):
    """Settings used to label method-specific diagnostics."""

    height: float
    eps: float
    min_samples: int


class PlotResult(TypedDict):
    """Common plotting result with optional algorithm-specific diagnostics."""

    labels: NDArray[np.integer]
    summary: pd.DataFrame
    silhouette: NDArray[np.float64]
    silhouette_reason: str
    parameters: PlotParameters
    linkage_matrix: NotRequired[NDArray[np.float64]]
    silhouette_by_k: NotRequired[pd.Series]
    neighbor_distances: NotRequired[NDArray[np.float64]]
    noise: NotRequired[int]
    n_groups: NotRequired[int]


class PlotCase(TypedDict):
    """Identified configuration for plotting and comparison."""

    name: str
    description: str
    result: PlotResult
