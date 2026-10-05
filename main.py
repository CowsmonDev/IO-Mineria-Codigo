"""Ejecuta las tres etapas del análisis en orden."""

import argparse
import sys

from src import analisis_extra, analisis_preliminar
from src.clustering.kmeans import analizar as analizar_kmeans
from src.data import manipulacion as manipulacion_datos


def main(analisis="extra"):
    print("\nEtapa 1/3: preparación de datos", flush=True)
    datos = manipulacion_datos.main()

    print("\nEtapa 2/3: análisis preliminar", flush=True)
    resultados_preliminares = analisis_preliminar.main(datos)

    if analisis == "kmeans":
        print("\nEtapa 3/3: comparación K-Means", flush=True)
        analizar_kmeans(resultados_preliminares)
    else:
        print("\nEtapa 3/3: análisis extra", flush=True)
        analisis_extra.main(resultados_preliminares)

    print("\nLas tres etapas finalizaron correctamente.", flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analisis", choices=["extra", "kmeans"], default="extra")
    sys.exit(main(parser.parse_args().analisis))
