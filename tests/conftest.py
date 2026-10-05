"""Entrada sintética común para las pruebas."""

import numpy as np
import pandas as pd
import pytest

from src.data.preparacion import estandarizar


@pytest.fixture
def entrada():
    rng = np.random.default_rng(22)
    grupos = np.repeat(np.arange(1, 8), 10)
    originales = pd.DataFrame(
        {
            "tiempo_desde_ingreso": grupos * 100 + rng.normal(0, 2, len(grupos)),
            "cursadas_aprobadas": grupos.astype(float) * 3,
            "cursadas_promocionadas": grupos.astype(float),
            "cursadas_desaprobadas": (grupos % 3).astype(float),
            "materias_anotado_ult_anio": (grupos % 4).astype(float),
            "finales_aprobados": grupos * 10 + rng.normal(0, 0.2, len(grupos)),
            "finales_desaprobados": (grupos % 2).astype(float),
            "dias_dsd_ultimo_final": grupos.astype(float) * 20,
            "porc_finales": grupos / 20,
            "deserto": (grupos > 4).astype(float),
        }
    )
    return {
        "originales": originales,
        "matriz": estandarizar(originales),
        "ids_alumnos": np.arange(200, 270),
        "fecha_analisis": "2026-10-01",
    }
