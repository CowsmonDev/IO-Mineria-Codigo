"""Figuras de líneas con una referencia opcional."""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


def graficar_lineas(
    x: ArrayLike,
    y: ArrayLike,
    *,
    titulo: str,
    xlabel: str,
    ylabel: str,
    marcador: str | None = None,
    referencia: float | None = None,
    etiqueta_referencia: str | None = None,
    tamano: tuple[float, float] = (9, 5),
) -> Figure:
    """Devuelve una curva y, si se pide, una línea horizontal de referencia."""
    fig, ax = plt.subplots(figsize=tamano)
    ax.plot(x, y, marker=marcador)
    if referencia is not None:
        ax.axhline(
            referencia,
            color="red",
            linestyle="--",
            label=etiqueta_referencia,
        )
        if etiqueta_referencia:
            ax.legend()
    ax.set(title=titulo, xlabel=xlabel, ylabel=ylabel)
    return fig
