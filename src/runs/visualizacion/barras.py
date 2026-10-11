"""Figuras de barras individuales y comparaciones en paneles."""

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


def graficar_barras(
    etiquetas: Sequence[str],
    valores: ArrayLike,
    *,
    titulo: str,
    xlabel: str,
    ylabel: str,
    ylim: tuple[float, float] | None = None,
) -> Figure:
    """Dibuja una serie de barras; devuelve la figura sin guardarla."""
    ancho = min(24, max(8, len(etiquetas) * 0.35))
    fig, ax = plt.subplots(figsize=(ancho, 5))
    ax.bar(etiquetas, valores)
    ax.set(title=titulo, xlabel=xlabel, ylabel=ylabel, ylim=ylim)
    if len(etiquetas) > 15:
        ax.tick_params(axis="x", labelrotation=90, labelsize=8)
    return fig


def graficar_comparacion_barras(
    etiquetas: Sequence[str],
    series: Sequence[tuple[str, ArrayLike]],
    *,
    titulo: str,
) -> Figure:
    """Dibuja un panel horizontal por cada par (título, valores)."""
    fig, axes = plt.subplots(1, len(series), figsize=(16, 6), squeeze=False)
    for ax, (titulo_panel, valores) in zip(axes[0], series):
        valores = np.asarray(valores)
        barras = ax.barh(etiquetas, valores)
        ax.bar_label(
            barras,
            labels=[f"{v:.1f}" if np.isfinite(v) else "Sin agrupados" for v in valores],
            padding=3,
        )
        finitos = [v for v in valores if np.isfinite(v)]
        ax.set(title=titulo_panel, xlim=(0, max([1, *finitos]) * 1.2))
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.2)
    fig.suptitle(titulo)
    return fig
