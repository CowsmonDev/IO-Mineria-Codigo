"""K-Means con siete grupos e inicialización reproducible."""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples

PARAMETROS = {
    "n_clusters": 7,
    "init": "k-means++",
    "n_init": 25,
    "random_state": 123,
    "algorithm": "lloyd",
    "max_iter": 300,
    "tol": 1e-4,
}


def analizar(matriz, originales):
    """Agrupa y devuelve Silhouette y medias en unidades originales."""
    x = np.asarray(matriz, dtype=float)
    if len(x) <= 7 or len(np.unique(x, axis=0)) < 7:
        raise ValueError(
            "No hay suficientes observaciones distintas para siete grupos."
        )
    modelo = KMeans(**PARAMETROS).fit(x)
    etiquetas = modelo.labels_ + 1
    silhouette = silhouette_samples(x, etiquetas)
    agrupados = (
        originales.reset_index(drop=True).assign(grupo=etiquetas).groupby("grupo")
    )
    resumen = agrupados.mean()
    resumen.insert(0, "cantidad", agrupados.size())
    return {
        "etiquetas": etiquetas,
        "resumen": resumen,
        "silhouette": silhouette,
        "silhouette_promedio": float(silhouette.mean()),
        "poblacion_silhouette": len(x),
        "motivo_silhouette": "",
        "inercia": float(modelo.inertia_),
        "centros": modelo.cluster_centers_,
        "parametros": dict(PARAMETROS),
    }
