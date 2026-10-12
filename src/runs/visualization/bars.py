"""Individual bar charts and comparison panels."""

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


def plot_bars(
    labels: Sequence[str],
    values: ArrayLike,
    *,
    title: str,
    xlabel: str,
    ylabel: str,
    ylim: tuple[float, float] | None = None,
) -> Figure:
    """Plot a bar series and return its figure without saving it."""
    width = min(24, max(8, len(labels) * 0.35))
    fig, ax = plt.subplots(figsize=(width, 5))
    ax.bar(labels, values)
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel, ylim=ylim)
    if len(labels) > 15:
        ax.tick_params(axis="x", labelrotation=90, labelsize=8)
    return fig


def plot_bar_comparison(
    labels: Sequence[str],
    series: Sequence[tuple[str, ArrayLike]],
    *,
    title: str,
) -> Figure:
    """Draw one horizontal panel per title/value pair."""
    fig, axes = plt.subplots(1, len(series), figsize=(16, 6), squeeze=False)
    for ax, (panel_title, values) in zip(axes[0], series):
        values = np.asarray(values)
        bars = ax.barh(labels, values)
        ax.bar_label(
            bars,
            labels=[
                f"{v:.1f}" if np.isfinite(v) else "No clustered students"
                for v in values
            ],
            padding=3,
        )
        finite_values = [v for v in values if np.isfinite(v)]
        ax.set(title=panel_title, xlim=(0, max([1, *finite_values]) * 1.2))
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.2)
    fig.suptitle(title)
    return fig
