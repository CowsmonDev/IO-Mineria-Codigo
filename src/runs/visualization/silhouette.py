"""Group Silhouette plot, including unavailable results."""

from textwrap import fill

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


def plot_silhouette(
    values: ArrayLike,
    labels: ArrayLike,
    *,
    title: str,
    reason: str = "",
) -> Figure:
    """Return sorted Silhouette values, excluding noise (-1)."""
    fig, ax = plt.subplots(figsize=(8, 6))
    values = np.asarray(values)
    labels = np.asarray(labels)
    if not np.isfinite(values).any():
        ax.text(
            0.5,
            0.5,
            fill(reason, width=48),
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        ax.set(title=f"{title}: Silhouette unavailable", yticks=[], xticks=[])
    else:
        start = 0
        for group in np.unique(labels):
            if group == -1:
                continue
            sorted_values = np.sort(values[labels == group])
            ax.fill_betweenx(
                np.arange(start, start + len(sorted_values)), 0, sorted_values
            )
            ax.text(-0.95, start + len(sorted_values) / 2, str(group))
            start += len(sorted_values) + 10
        n = np.isfinite(values).sum()
        ax.axvline(np.nanmean(values), color="red", linestyle="--")
        ax.set(
            title=f"{title}: Silhouette {np.nanmean(values):.4f}\n{n}/{len(values)} students",
            xlim=(-1, 1),
            xlabel="Silhouette",
            yticks=[],
        )
    return fig
