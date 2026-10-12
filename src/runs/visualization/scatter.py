"""Scatter plots for dropout diagnostics."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from numpy.typing import ArrayLike

from src.data.constants import Columns


def plot_dropout_by_group(
    values: pd.Series,
    groups: ArrayLike,
    *,
    title: str,
    rng: np.random.Generator | None = None,
) -> Figure:
    """Add reproducible jitter to separate overlapping observations."""
    rng = np.random.default_rng(1) if rng is None else rng
    fig, ax = plt.subplots(figsize=(8, 6))
    groups = np.asarray(groups)
    for position, group in enumerate(np.unique(groups)):
        data = values.loc[groups == group].to_numpy()
        ax.scatter(
            data + rng.uniform(-0.15, 0.15, len(data)),
            position + rng.uniform(-0.25, 0.25, len(data)),
            alpha=0.75,
        )
    ax.set(
        title=title,
        xlabel="Dropout (1: yes; 0: no)",
        ylabel="Cluster",
        xticks=[0, 1],
        yticks=range(len(np.unique(groups))),
        yticklabels=np.unique(groups),
    )
    return fig


def plot_progress_vs_promoted_courses(
    original_values: pd.DataFrame,
    *,
    title: str,
    rng: np.random.Generator | None = None,
) -> Figure:
    """Compare progress and promoted courses by dropout status."""
    rng = np.random.default_rng(1) if rng is None else rng
    fig, ax = plt.subplots(figsize=(9, 6))
    for value, data in original_values.groupby(Columns.DROPPED_OUT):
        ax.scatter(
            data[Columns.PROMOTED_COURSES] + rng.uniform(-0.3, 0.3, len(data)),
            data[Columns.FINAL_COMPLETION_RATIO] + rng.uniform(-0.05, 0.05, len(data)),
            alpha=0.8,
            label=str(int(value)),
        )
    ax.set(title=title, xlabel="Promoted courses", ylabel="Degree progress")
    ax.legend(title="Dropout (1: yes; 0: no)")
    return fig
