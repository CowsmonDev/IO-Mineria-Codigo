"""Prepara datos, ejecuta tres algoritmos y genera sus gráficos."""

import argparse
import os
from pathlib import Path

import pandas as pd

from src.clustering import dbscan, jerarquico, kmeans
from src.data.preparacion import preparar_entrada, validar_entrada
from src.visualizacion import generar

RAIZ = Path(__file__).resolve().parent
FECHA_REFERENCIA = "2026-10-01"


def main(*, fecha=None, salida=None, eps=dbscan.EPS, min_samples=dbscan.MIN_SAMPLES):
    """Prepara la entrada común, ejecuta los métodos y genera sus salidas."""
    fecha = (
        pd.Timestamp(fecha or os.environ.get("ANALYSIS_DATE") or FECHA_REFERENCIA)
        .date()
        .isoformat()
    )
    salida = Path(salida) if salida is not None else RAIZ / "output"
    print(f"Etapa 1/5: preparación común (fecha {fecha})", flush=True)
    entrada = preparar_entrada(fecha_analisis=fecha)

    validar_entrada(entrada)
    matriz = entrada["matriz"].to_numpy(dtype=float, copy=True)
    originales = entrada["originales"]
    print("Etapa 2/5: jerárquico de referencia", flush=True)
    resultados = {"jerarquico": jerarquico.analizar(matriz, originales)}
    print("Etapa 3/5: K-Means", flush=True)
    resultados["kmeans"] = kmeans.analizar(matriz, originales)
    print(f"Etapa 4/5: DBSCAN (eps={eps}, min_samples={min_samples})", flush=True)
    resultados["dbscan"] = dbscan.analizar(
        matriz, originales, eps=eps, min_samples=min_samples
    )
    print("Etapa 5/5: gráficos", flush=True)
    generar(entrada, resultados, Path(salida))
    jerarquico.guardar_resumen(resultados["jerarquico"], Path(salida) / "jerarquico")
    for metodo, resultado in resultados.items():
        print(f"\n{metodo}: {resultado['parametros']}")
        print(resultado["resumen"].to_string())
        if resultado["motivo_silhouette"]:
            print(resultado["motivo_silhouette"])
        else:
            print(
                f"Silhouette: {resultado['silhouette_promedio']:.6f} sobre {resultado['poblacion_silhouette']} estudiantes"
            )
        if metodo == "dbscan":
            print(f"Ruido: {resultado['ruido']}/{len(matriz)} estudiantes")
    print(f"\nGráficos guardados en: {Path(salida).resolve()}")
    return {"entrada": entrada, "resultados": resultados}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fecha",
        help=f"Fecha de análisis; por defecto ANALYSIS_DATE o {FECHA_REFERENCIA}.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        help="Carpeta raíz de resultados; contiene <método>/graficos/.",
    )
    parser.add_argument(
        "--eps", type=float, default=dbscan.EPS, help="Radio DBSCAN (por defecto 1.5)."
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=dbscan.MIN_SAMPLES,
        help="Mínimo de vecinos DBSCAN, incluido el propio punto (por defecto 5).",
    )
    args = parser.parse_args()
    main(
        fecha=args.fecha, salida=args.salida, eps=args.eps, min_samples=args.min_samples
    )
