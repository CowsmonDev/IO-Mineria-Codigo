"""Contrato de entrada y salidas de la comparación K-Means."""

import json

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import adjusted_rand_score

from src.clustering.kmeans import SEMILLAS, _validar, analizar
from src.data.preparacion import estandarizar


@pytest.fixture
def datos():
    rng = np.random.default_rng(22)
    grupos = np.repeat(np.arange(1, 8), 10)
    originales = pd.DataFrame(
        {
            "finales_aprobados": grupos * 10 + rng.normal(0, 0.2, len(grupos)),
            "tiempo_desde_ingreso": grupos * 100 + rng.normal(0, 2, len(grupos)),
            "deserto": (grupos > 4).astype(float),
        },
        index=np.arange(100, 170),
    )
    matriz = estandarizar(originales)
    originales["cluster"] = pd.Categorical(grupos)
    return {
        "alumnos_s_avanzados": originales,
        "alumnos_s_avanzados_sc": matriz,
        "ids_alumnos": np.arange(200, 270),
        "fecha_analisis": "2026-10-01",
    }


def test_rechaza_filas_reordenadas(datos):
    datos["alumnos_s_avanzados_sc"] = datos["alumnos_s_avanzados_sc"].iloc[::-1]
    with pytest.raises(ValueError, match="orden"):
        _validar(datos)


def test_rechaza_etiquetas_como_variable(datos):
    datos["alumnos_s_avanzados_sc"]["cluster"] = 1
    with pytest.raises(ValueError, match="etiquetas"):
        _validar(datos)


def test_rechaza_identidades_duplicadas(datos):
    datos["ids_alumnos"][1] = datos["ids_alumnos"][0]
    with pytest.raises(ValueError, match="único"):
        _validar(datos)


def test_exporta_comparacion_sin_mutar_entrada(datos, tmp_path):
    original = datos["alumnos_s_avanzados"].copy(deep=True)
    matriz = datos["alumnos_s_avanzados_sc"].copy(deep=True)
    salida, graficos = tmp_path / "tablas", tmp_path / "graficos"
    resultado = analizar(datos, directorio=salida, directorio_graficos=graficos)
    pd.testing.assert_frame_equal(datos["alumnos_s_avanzados"], original)
    pd.testing.assert_frame_equal(datos["alumnos_s_avanzados_sc"], matriz)
    asignaciones = pd.read_csv(salida / "asignaciones.csv")
    np.testing.assert_array_equal(asignaciones["id_alumno"], datos["ids_alumnos"])
    assert asignaciones["cluster_kmeans"].nunique() == 7
    assert (
        adjusted_rand_score(
            asignaciones["cluster_jerarquico"], asignaciones["cluster_kmeans"]
        )
        == 1
    )
    assert resultado["correspondencia"].to_numpy().sum() == len(original)
    assert len(resultado["estabilidad"]) == len(SEMILLAS)
    assert resultado["estabilidad"]["ari_con_principal"].min() == 1
    configuracion = json.loads((salida / "configuracion.json").read_text())
    assert configuracion["fecha_analisis"] == "2026-10-01"
    assert configuracion["variables"] == list(matriz.columns)
    assert len(list(graficos.glob("*.png"))) == 6
    assert len(list(salida.glob("*.csv"))) == 10
