"""Ejecución independiente de la regresión logística LASSO."""

from src.data.preparacion import preparar_entrada
from src.methods.lasso import analizar


def main(*, fecha_analisis=None):
    """Ejecuta el antecedente LASSO por separado de la comparación."""
    entrada = preparar_entrada(fecha_analisis=fecha_analisis)
    return analizar(entrada["originales"])


if __name__ == "__main__":
    main()
