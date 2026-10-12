"""Overall dendrograms and internal group diagnostics."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from numpy.typing import ArrayLike
from scipy.cluster.hierarchy import cut_tree, dendrogram, linkage
from scipy.spatial.distance import pdist


def plot_dendrogram(
    linkage_matrix: ArrayLike,
    *,
    title: str,
    cut_height: float,
    ylim: tuple[float, float] | None = None,
) -> Figure:
    """Draw a computed linkage and mark the cut height."""
    fig, ax = plt.subplots(figsize=(10, 6))
    dendrogram(linkage_matrix, color_threshold=cut_height, no_labels=True, ax=ax)
    ax.axhline(cut_height, linestyle="--", color="red")
    ax.set(title=title, ylabel="Height", ylim=ylim)
    return fig


def plot_internal_dendrogram(
    data: pd.DataFrame,
    *,
    title: str,
    subgroups: int,
    size: tuple[float, float] = (15, 10),
    labels: bool = False,
) -> Figure:
    """Recompute Ward on a subset and mark diagnostic subgroups."""
    linkage_matrix = linkage(pdist(data.to_numpy()), method="ward")
    fig, ax = plt.subplots(figsize=size)
    drawing = dendrogram(
        linkage_matrix,
        no_labels=not labels,
        labels=data.index.astype(str).tolist() if labels else None,
        leaf_font_size=7,
        ax=ax,
    )
    ax.set(title=title, ylabel="Height (distance)")
    k = min(subgroups, len(data))
    groups = cut_tree(linkage_matrix, n_clusters=k).reshape(-1)
    positions = {leaf: 5 + i * 10 for i, leaf in enumerate(drawing["leaves"])}
    order = sorted(
        np.unique(groups),
        key=lambda group: min(positions[i] for i in np.flatnonzero(groups == group)),
    )
    upper = linkage_matrix[len(data) - k, 2]
    lower = linkage_matrix[len(data) - k - 1, 2] if len(data) > k else 0
    height = (upper + lower) / 2
    for group, color in zip(order, ("red", "green", "blue", "cyan")):
        xs = [positions[i] for i in np.flatnonzero(groups == group)]
        ax.add_patch(
            Rectangle(
                (min(xs) - 4, 0),
                max(xs) - min(xs) + 8,
                height,
                fill=False,
                edgecolor=color,
            )
        )
    return fig
