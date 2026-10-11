"""DBSCAN con parámetros explícitos y diagnóstico de distancias a vecinos."""

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_samples
from sklearn.neighbors import NearestNeighbors

EPS = 1.5
MIN_SAMPLES = 5


def analizar(matriz, originales, *, eps=EPS, min_samples=MIN_SAMPLES):
    """Ejecuta una configuración; el ruido -1 se excluye solo de Silhouette."""
    x = np.asarray(matriz, dtype=float)
    if (
        not np.isfinite(eps)
        or eps <= 0
        or not isinstance(min_samples, int)
        or not 2 <= min_samples <= len(x)
    ):
        raise ValueError("Se requiere eps positivo y finito y 2 <= min_samples <= n.")
    modelo = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean").fit(x)
    etiquetas = np.where(modelo.labels_ == -1, -1, modelo.labels_ + 1)
    incluidos = etiquetas != -1
    n = int(incluidos.sum())
    k = len(np.unique(etiquetas[incluidos]))
    silhouette = np.full(len(x), np.nan)
    motivo = ""
    if 2 <= k < n:
        silhouette[incluidos] = silhouette_samples(x[incluidos], etiquetas[incluidos])
    else:
        motivo = f"Silhouette no disponible: {k} grupos y {n} estudiantes sin ruido; se requieren entre 2 y n-1 grupos."
    agrupados = (
        originales.reset_index(drop=True).assign(grupo=etiquetas).groupby("grupo")
    )
    resumen = agrupados.mean()
    resumen.insert(0, "cantidad", agrupados.size())
    # kneighbors(X) incluye al propio punto: para m corresponde la columna m-1.
    distancias = (
        NearestNeighbors(n_neighbors=min_samples, metric="euclidean")
        .fit(x)
        .kneighbors(x)[0][:, min_samples - 1]
    )
    return {
        "etiquetas": etiquetas,
        "resumen": resumen,
        "silhouette": silhouette,
        "silhouette_promedio": float(np.nanmean(silhouette)) if not motivo else np.nan,
        "poblacion_silhouette": n if not motivo else 0,
        "motivo_silhouette": motivo,
        "ruido": int((~incluidos).sum()),
        "grupos": k,
        "distancias_vecinos": np.sort(distancias),
        "parametros": {"eps": eps, "min_samples": min_samples, "metric": "euclidean"},
    }
