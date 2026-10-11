"""Ejecución individual y casos fijos de DBSCAN con sus salidas."""

from pathlib import Path

import pandas as pd

from src.methods import dbscan
from src.runs._salidas import imprimir_resultado
from src.runs.visualizacion.visualizacion import (
    generar_graficos_experimentos_dbscan,
    generar_graficos_metodos,
)

EPS = dbscan.EPS
MIN_SAMPLES = dbscan.MIN_SAMPLES

# Casos representativos de la exploración; no es una búsqueda ni una selección.
CONFIGURACIONES_PRUEBAS = (
    ("referencia", "Configuración original", 1.5, 5),
    ("siete_poco_ruido", "Siete grupos con poco ruido", 1.175, 4),
    ("siete_mas_ruido", "Siete grupos con más ruido", 0.5, 10),
    ("catorce_grupos", "Mayor cantidad de grupos", 0.5, 6),
    ("fragmentacion", "Radio pequeño y alta fragmentación", 0.18, 5),
)


def pruebas(entrada, directorio, *, eps=EPS, min_samples=MIN_SAMPLES):
    """Ejecuta la configuración solicitada y los cinco casos del informe.

    Los nombres describen lo observado en la fecha de referencia, no garantizan
    una cantidad de grupos al cambiar los datos o la fecha.
    """
    matriz, originales = entrada["matriz"], entrada["originales"]
    resultado = dbscan.analizar(matriz, originales, eps=eps, min_samples=min_samples)
    casos = [
        {
            "nombre": nombre,
            "descripcion": descripcion,
            "resultado": (
                resultado
                if (eps, min_samples) == (radio, minimo)
                else dbscan.analizar(matriz, originales, eps=radio, min_samples=minimo)
            ),
        }
        for nombre, descripcion, radio, minimo in CONFIGURACIONES_PRUEBAS
    ]
    directorio = Path(directorio)
    generar_graficos_metodos(entrada, {"dbscan": resultado}, directorio)
    generar_graficos_experimentos_dbscan(entrada, casos, directorio)
    imprimir_resultado("dbscan", resultado)
    filas = []
    for caso in casos:
        r = caso["resultado"]
        tamanos = r["resumen"].drop(index=-1, errors="ignore")["cantidad"]
        filas.append(
            {
                "caso": caso["nombre"],
                **r["parametros"],
                "grupos": r["grupos"],
                "ruido_pct": 100 * r["ruido"] / len(matriz),
                "mayor_pct_agrupados": (
                    100 * tamanos.max() / tamanos.sum()
                    if len(tamanos)
                    else float("nan")
                ),
                "silhouette_sin_ruido": r["silhouette_promedio"],
                "evaluados_silhouette": r["poblacion_silhouette"],
            }
        )
        imprimir_resultado(f"DBSCAN — {caso['descripcion']}", r)
    print("\nDBSCAN — comparación de casos fijos (grupo mayor excluye ruido):")
    print(pd.DataFrame(filas).to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    return {"resultado": resultado, "casos": casos}
