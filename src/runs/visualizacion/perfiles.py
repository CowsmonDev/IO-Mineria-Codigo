"""Distribución de una variable original dentro de cada grupo."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


def graficar_perfil(
    originales: pd.DataFrame,
    etiquetas: ArrayLike,
    variable: str,
    *,
    titulo: str,
    horizontal: bool = False,
) -> Figure:
    """Dibuja boxplots por grupo sin modificar la tabla de entrada."""
    grupos = ["Ruido" if grupo == -1 else str(grupo) for grupo in np.asarray(etiquetas)]
    ancho = min(24, max(8, len(set(grupos)) * 0.35))
    fig, ax = plt.subplots(figsize=(ancho, 6))
    tabla = originales[[variable]].reset_index(drop=True).assign(grupo=grupos)
    if horizontal:
        sns.boxplot(data=tabla, x=variable, y="grupo", orient="h", ax=ax)
        ax.set(xlabel=variable, ylabel="Grupo")
    else:
        sns.boxplot(data=tabla, x="grupo", y=variable, ax=ax)
        ax.set(xlabel="Grupo", ylabel=variable)
        if tabla["grupo"].nunique() > 15:
            ax.tick_params(axis="x", labelrotation=90, labelsize=8)
    ax.set(title=titulo)
    return fig
