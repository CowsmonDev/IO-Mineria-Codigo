"""Entrada común y conservación del protocolo K-Means."""

import numpy as np
import pytest
from sklearn.metrics import adjusted_rand_score

from src.clustering.kmeans import analizar
from src.data.preparacion import validar_entrada


def test_rechaza_filas_reordenadas(entrada):
    entrada["matriz"] = entrada["matriz"].iloc[::-1]
    with pytest.raises(ValueError, match="orden"):
        validar_entrada(entrada)


def test_rechaza_etiquetas_como_variable(entrada):
    entrada["matriz"]["cluster"] = 1
    with pytest.raises(ValueError, match="etiquetas"):
        validar_entrada(entrada)


def test_rechaza_identidades_duplicadas(entrada):
    entrada["ids_alumnos"][1] = entrada["ids_alumnos"][0]
    with pytest.raises(ValueError, match="único"):
        validar_entrada(entrada)


def test_kmeans_separa_perfiles_y_no_muta_entrada(entrada):
    matriz = entrada["matriz"].to_numpy(copy=True)
    resultado = analizar(matriz, entrada["originales"])
    np.testing.assert_array_equal(matriz, entrada["matriz"].to_numpy())
    assert len(np.unique(resultado["etiquetas"])) == 7
    assert adjusted_rand_score(np.repeat(range(7), 10), resultado["etiquetas"]) == 1
    assert resultado["parametros"]["random_state"] == 123
    assert resultado["resumen"]["cantidad"].sum() == len(matriz)
    assert resultado["poblacion_silhouette"] == len(matriz)
