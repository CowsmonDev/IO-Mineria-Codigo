"""Referencia fija: distancia euclídea, enlace Ward y corte a altura 35."""

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import cut_tree, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import silhouette_samples, silhouette_score


def analizar(matriz, originales):
    """Devuelve agrupamiento original, Silhouette y medias por grupo."""
    x = np.asarray(matriz, dtype=float)
    distancias = pdist(x, metric="euclidean")
    enlace = linkage(distancias, method="ward")
    etiquetas = cut_tree(enlace, height=35).reshape(-1) + 1
    if len(np.unique(etiquetas)) != 7:
        raise ValueError(
            "El corte a altura 35 no reproduce los siete grupos de referencia."
        )
    distancias_cuadradas = squareform(distancias)
    silhouette = silhouette_samples(
        distancias_cuadradas, etiquetas, metric="precomputed"
    )
    # Diagnóstico del original R; no cambia el corte fijo a altura 35.
    silhouette_por_k = pd.Series(
        {
            k: silhouette_score(
                distancias_cuadradas,
                cut_tree(enlace, n_clusters=k).reshape(-1),
                metric="precomputed",
            )
            for k in range(2, min(16, len(x)))
        },
        name="silhouette",
    )
    silhouette_por_k.index.name = "k"
    agrupados = (
        originales.reset_index(drop=True).assign(grupo=etiquetas).groupby("grupo")
    )
    resumen = agrupados.mean()
    resumen.insert(0, "cantidad", agrupados.size())
    return {
        "etiquetas": etiquetas,
        "enlace": enlace,
        "resumen": resumen,
        "silhouette": silhouette,
        "silhouette_promedio": float(silhouette.mean()),
        "silhouette_por_k": silhouette_por_k,
        "poblacion_silhouette": len(x),
        "motivo_silhouette": "",
        "parametros": {"metric": "euclidean", "method": "ward", "height": 35},
    }
