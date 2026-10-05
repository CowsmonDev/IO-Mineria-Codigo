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
            "finales_aprobados": grupos * 10 + rng.normal(0, 0.2, len(grupos)),
            "tiempo_desde_ingreso": grupos * 100 + rng.normal(0, 2, len(grupos)),
            "deserto": (grupos > 4).astype(float),
        }
    )
    return {
        "originales": originales,
        "matriz": estandarizar(originales),
        "ids_alumnos": np.arange(200, 270),
        "fecha_analisis": "2026-10-01",
    }
