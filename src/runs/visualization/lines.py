"""Line charts with optional reference values."""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


def plot_lines(
    x: ArrayLike,
    y: ArrayLike,
    *,
    title: str,
    xlabel: str,
    ylabel: str,
    marker: str | None = None,
    reference: float | None = None,
    reference_label: str | None = None,
    size: tuple[float, float] = (9, 5),
) -> Figure:
    """Return a curve with an optional horizontal reference line."""
    fig, ax = plt.subplots(figsize=size)
    ax.plot(x, y, marker=marker)
    if reference is not None:
        ax.axhline(
            reference,
            color="red",
            linestyle="--",
            label=reference_label,
        )
        if reference_label:
            ax.legend()
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    return fig
