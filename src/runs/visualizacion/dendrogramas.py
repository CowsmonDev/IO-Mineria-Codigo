"""Dendrogramas generales y diagnósticos internos de los grupos."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from numpy.typing import ArrayLike
from scipy.cluster.hierarchy import cut_tree, dendrogram, linkage
from scipy.spatial.distance import pdist


def graficar_dendrograma(
    enlace: ArrayLike,
    *,
    titulo: str,
    altura_corte: float,
    ylim: tuple[float, float] | None = None,
) -> Figure:
    """Dibuja un enlace ya calculado y marca la altura de corte."""
    fig, ax = plt.subplots(figsize=(10, 6))
    dendrogram(enlace, color_threshold=altura_corte, no_labels=True, ax=ax)
    ax.axhline(altura_corte, linestyle="--", color="red")
    ax.set(title=titulo, ylabel="Altura", ylim=ylim)
    return fig


def graficar_dendrograma_interno(
    datos: pd.DataFrame,
    *,
    titulo: str,
    subgrupos: int,
    tamano: tuple[float, float] = (15, 10),
    etiquetas: bool = False,
) -> Figure:
    """Recalcula Ward para el subconjunto y señala subgrupos diagnósticos."""
    enlace = linkage(pdist(datos.to_numpy()), method="ward")
    fig, ax = plt.subplots(figsize=tamano)
    dibujo = dendrogram(
        enlace,
        no_labels=not etiquetas,
        labels=datos.index.astype(str).tolist() if etiquetas else None,
        leaf_font_size=7,
        ax=ax,
    )
    ax.set(title=titulo, ylabel="Altura (distancia)")
    k = min(subgrupos, len(datos))
    grupos = cut_tree(enlace, n_clusters=k).reshape(-1)
    posiciones = {hoja: 5 + i * 10 for i, hoja in enumerate(dibujo["leaves"])}
    orden = sorted(
        np.unique(grupos),
        key=lambda grupo: min(posiciones[i] for i in np.flatnonzero(grupos == grupo)),
    )
    superior = enlace[len(datos) - k, 2]
    inferior = enlace[len(datos) - k - 1, 2] if len(datos) > k else 0
    altura = (superior + inferior) / 2
    for grupo, color in zip(orden, ("red", "green", "blue", "cyan")):
        xs = [posiciones[i] for i in np.flatnonzero(grupos == grupo)]
        ax.add_patch(
            Rectangle(
                (min(xs) - 4, 0),
                max(xs) - min(xs) + 8,
                altura,
                fill=False,
                edgecolor=color,
            )
        )
    return fig
