"""Figuras de dispersión para diagnósticos de deserción."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


def graficar_desercion_por_grupo(
    valores: pd.Series,
    grupos: ArrayLike,
    *,
    titulo: str,
    rng: np.random.Generator | None = None,
) -> Figure:
    """Añade desplazamientos reproducibles para separar puntos superpuestos."""
    rng = np.random.default_rng(1) if rng is None else rng
    fig, ax = plt.subplots(figsize=(8, 6))
    grupos = np.asarray(grupos)
    for posicion, grupo in enumerate(np.unique(grupos)):
        datos = valores.loc[grupos == grupo].to_numpy()
        ax.scatter(
            datos + rng.uniform(-0.15, 0.15, len(datos)),
            posicion + rng.uniform(-0.25, 0.25, len(datos)),
            alpha=0.75,
        )
    ax.set(
        title=titulo,
        xlabel="Deserto (1: sí; 0: no)",
        ylabel="Cluster",
        xticks=[0, 1],
        yticks=range(len(np.unique(grupos))),
        yticklabels=np.unique(grupos),
    )
    return fig


def graficar_avance_vs_promocionadas(
    originales: pd.DataFrame,
    *,
    titulo: str,
    rng: np.random.Generator | None = None,
) -> Figure:
    """Compara avance y promocionadas, distinguiendo la deserción."""
    rng = np.random.default_rng(1) if rng is None else rng
    fig, ax = plt.subplots(figsize=(9, 6))
    for valor, datos in originales.groupby("deserto"):
        ax.scatter(
            datos["cursadas_promocionadas"] + rng.uniform(-0.3, 0.3, len(datos)),
            datos["porc_finales"] + rng.uniform(-0.05, 0.05, len(datos)),
            alpha=0.8,
            label=str(int(valor)),
        )
    ax.set(title=titulo, xlabel="Cursadas promocionadas", ylabel="Avance de carrera")
    ax.legend(title="Deserto (1: sí; 0: no)")
    return fig
