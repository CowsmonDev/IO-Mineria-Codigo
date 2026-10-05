"""Referencia fija: distancia euclídea, enlace Ward y corte a altura 35."""

import numpy as np
from scipy.cluster.hierarchy import cut_tree, linkage
from scipy.spatial.distance import pdist
from sklearn.metrics import silhouette_samples


def analizar(matriz, originales):
    """Devuelve agrupamiento original, Silhouette y medias por grupo."""
    x = np.asarray(matriz, dtype=float)
    enlace = linkage(pdist(x, metric="euclidean"), method="ward")
    etiquetas = cut_tree(enlace, height=35).reshape(-1) + 1
    if len(np.unique(etiquetas)) != 7:
        raise ValueError(
            "El corte a altura 35 no reproduce los siete grupos de referencia."
        )
    silhouette = silhouette_samples(x, etiquetas)
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
        "poblacion_silhouette": len(x),
        "motivo_silhouette": "",
        "parametros": {"metric": "euclidean", "method": "ward", "height": 35},
    }
