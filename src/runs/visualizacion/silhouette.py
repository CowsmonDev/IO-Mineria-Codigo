"""Figura de Silhouette por grupo, incluyendo el caso no disponible."""

from textwrap import fill

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


def graficar_silhouette(
    valores: ArrayLike,
    etiquetas: ArrayLike,
    *,
    titulo: str,
    motivo: str = "",
) -> Figure:
    """Devuelve una figura con los valores ordenados; excluye el ruido (-1)."""
    fig, ax = plt.subplots(figsize=(8, 6))
    valores = np.asarray(valores)
    etiquetas = np.asarray(etiquetas)
    if not np.isfinite(valores).any():
        ax.text(
            0.5,
            0.5,
            fill(motivo, width=48),
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        ax.set(title=f"{titulo}: Silhouette no disponible", yticks=[], xticks=[])
    else:
        inicio = 0
        for grupo in np.unique(etiquetas):
            if grupo == -1:
                continue
            ordenados = np.sort(valores[etiquetas == grupo])
            ax.fill_betweenx(np.arange(inicio, inicio + len(ordenados)), 0, ordenados)
            ax.text(-0.95, inicio + len(ordenados) / 2, str(grupo))
            inicio += len(ordenados) + 10
        n = np.isfinite(valores).sum()
        ax.axvline(np.nanmean(valores), color="red", linestyle="--")
        ax.set(
            title=f"{titulo}: Silhouette {np.nanmean(valores):.4f}\n{n}/{len(valores)} estudiantes",
            xlim=(-1, 1),
            xlabel="Silhouette",
            yticks=[],
        )
    return fig
