"""Distribution of an original feature within each group."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from numpy.typing import ArrayLike

from src.data.constants import Columns


def plot_profile(
    original_values: pd.DataFrame,
    labels: ArrayLike,
    variable: str,
    *,
    title: str,
    horizontal: bool = False,
) -> Figure:
    """Draw group boxplots without changing the input table."""
    groups = ["Noise" if group == -1 else str(group) for group in np.asarray(labels)]
    width = min(24, max(8, len(set(groups)) * 0.35))
    fig, ax = plt.subplots(figsize=(width, 6))
    table = (
        original_values[[variable]]
        .reset_index(drop=True)
        .assign(**{Columns.GROUP: groups})
    )
    if horizontal:
        sns.boxplot(data=table, x=variable, y=Columns.GROUP, orient="h", ax=ax)
        ax.set(xlabel=variable, ylabel="Group")
    else:
        sns.boxplot(data=table, x=Columns.GROUP, y=variable, ax=ax)
        ax.set(xlabel="Group", ylabel=variable)
        if table[Columns.GROUP].nunique() > 15:
            ax.tick_params(axis="x", labelrotation=90, labelsize=8)
    ax.set(title=title)
    return fig
