"""DBSCAN explícito, ruido y cálculo de Silhouette cuando corresponde."""

import numpy as np
import pandas as pd
import pytest
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors

from src.clustering.dbscan import analizar


@pytest.fixture
def matriz():
    rng = np.random.default_rng(8)
    return np.vstack(
        [rng.normal(-2, 0.03, (25, 2)), rng.normal(2, 0.03, (25, 2)), [[20, 20]]]
    )


def test_conserva_ruido_y_excluye_solo_de_silhouette(matriz):
    originales = pd.DataFrame(matriz, columns=["a", "b"])
    resultado = analizar(matriz, originales, eps=0.2, min_samples=5)
    esperado = DBSCAN(eps=0.2, min_samples=5).fit(matriz)
    np.testing.assert_array_equal(
        resultado["etiquetas"],
        np.where(esperado.labels_ == -1, -1, esperado.labels_ + 1),
    )
    assert resultado["ruido"] == 1 and resultado["grupos"] == 2
    assert resultado["poblacion_silhouette"] == 50
    assert np.isnan(resultado["silhouette"][-1])
    assert resultado["silhouette_promedio"] == pytest.approx(
        silhouette_score(matriz[:-1], resultado["etiquetas"][:-1])
    )
    assert resultado["resumen"].loc[-1, "cantidad"] == 1
    assert resultado["resumen"]["cantidad"].sum() == len(matriz)


def test_vecinos_incluyen_el_propio_punto(matriz):
    resultado = analizar(matriz, pd.DataFrame(matriz))
    esperadas = NearestNeighbors(n_neighbors=5).fit(matriz).kneighbors(matriz)[0][:, 4]
    np.testing.assert_allclose(resultado["distancias_vecinos"], np.sort(esperadas))


@pytest.mark.parametrize("eps", [1e-12, 100])
def test_todo_ruido_o_un_solo_grupo_no_interrumpen_el_analisis(matriz, eps):
    resultado = analizar(matriz, pd.DataFrame(matriz), eps=eps, min_samples=5)
    assert np.isnan(resultado["silhouette_promedio"])
    assert resultado["motivo_silhouette"]
    assert resultado["poblacion_silhouette"] == 0
    assert resultado["grupos"] == (0 if eps == 1e-12 else 1)


@pytest.mark.parametrize(
    "eps,min_samples", [(0, 5), (float("nan"), 5), (1.5, 1), (1.5, 100)]
)
def test_rechaza_parametros_invalidos(matriz, eps, min_samples):
    with pytest.raises(ValueError, match="Se requiere"):
        analizar(matriz, pd.DataFrame(matriz), eps=eps, min_samples=min_samples)
