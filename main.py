"""Ejecuta las tres etapas del análisis en orden."""

import sys

from src import analisis_extra, analisis_preliminar, manipulacion_datos


def main():
    print("\nEtapa 1/3: preparación de datos", flush=True)
    datos = manipulacion_datos.main()

    print("\nEtapa 2/3: análisis preliminar", flush=True)
    resultados_preliminares = analisis_preliminar.main(datos)

    print("\nEtapa 3/3: análisis extra", flush=True)
    analisis_extra.main(resultados_preliminares)

    print("\nLas tres etapas finalizaron correctamente.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
