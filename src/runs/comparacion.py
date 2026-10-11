"""Prepara la entrada común y coordina las pruebas de cada método."""

import os
from pathlib import Path

import pandas as pd

from src.data.preparacion import preparar_entrada, validar_entrada
from src.runs import dbscan, jerarquico, kmeans

RAIZ = Path(__file__).resolve().parents[2]
FECHA_REFERENCIA = "2026-10-01"


def main(*, fecha=None, salida=None, eps=dbscan.EPS, min_samples=dbscan.MIN_SAMPLES):
    """Delega métodos y salidas a los runs, conservando una entrada común."""
    fecha = (
        pd.Timestamp(fecha or os.environ.get("ANALYSIS_DATE") or FECHA_REFERENCIA)
        .date()
        .isoformat()
    )
    salida = Path(salida) if salida is not None else RAIZ / "output"
    print(f"Etapa 1/4: preparación común (fecha {fecha})", flush=True)
    entrada = preparar_entrada(fecha_analisis=fecha)
    validar_entrada(entrada)

    print("Etapa 2/4: pruebas y salidas del jerárquico", flush=True)
    ejecucion_jerarquico = jerarquico.pruebas(entrada, salida)
    print("Etapa 3/4: pruebas y salidas de K-Means", flush=True)
    ejecucion_kmeans = kmeans.pruebas(entrada, salida)
    print(
        f"Etapa 4/4: pruebas y salidas de DBSCAN (eps={eps}, min_samples={min_samples})",
        flush=True,
    )
    ejecucion_dbscan = dbscan.pruebas(entrada, salida, eps=eps, min_samples=min_samples)
    print(f"\nGráficos guardados en: {salida.resolve()}")
    return {
        "entrada": entrada,
        "resultados": {
            "jerarquico": ejecucion_jerarquico["resultado"],
            "kmeans": ejecucion_kmeans["resultado"],
            "dbscan": ejecucion_dbscan["resultado"],
        },
        "pruebas_dbscan": ejecucion_dbscan["casos"],
    }
