"""Entrada de consola para la comparación de agrupamientos."""

import argparse
from pathlib import Path

from src.runs import dbscan
from src.runs.comparacion import FECHA_REFERENCIA, main

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
