"""Membership heatmap normalized within each reference group."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure


def plot_correspondence(table: pd.DataFrame, *, title: str) -> Figure:
    """Show counts and row percentages; method labels are independent."""
    if table.empty or (table.sum(axis=1) <= 0).any():
        raise ValueError("The table must contain groups with members.")
    percentages = table.div(table.sum(axis=1), axis=0) * 100
    figure, ax = plt.subplots(figsize=(max(9, table.shape[1] * 1.2), 7))
    image = ax.imshow(percentages, cmap="Blues", vmin=0, vmax=100, aspect="auto")
    for i, j in np.ndindex(table.shape):
        percentage = percentages.iloc[i, j]
        ax.text(
            j,
            i,
            f"{int(table.iloc[i, j])}\n{percentage:.1f}%",
            ha="center",
            va="center",
            fontsize=9,
            color="white" if percentage > 55 else "black",
        )
    ax.set_xticks(range(table.shape[1]), [f"K{g}" for g in table.columns])
    ax.set_yticks(
        range(table.shape[0]),
        [f"J{g} (n={int(table.loc[g].sum())})" for g in table.index],
    )
    ax.set_xlabel("K-Means group (independent labels)")
    ax.set_ylabel("Hierarchical reference group")
    ax.set_title(title)
    figure.colorbar(
        image, ax=ax, label="Percentage within the hierarchical group (row)"
    )
    return figure
