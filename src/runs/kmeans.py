"""Ejecución de K-Means y generación de sus salidas."""

from pathlib import Path

from src.methods import kmeans
from src.runs._salidas import imprimir_resultado
from src.runs.visualizacion.visualizacion import generar_graficos_metodos


def pruebas(entrada, directorio):
    """Ejecuta la configuración actual; todavía no explora otros valores de k."""
    resultado = kmeans.analizar(entrada["matriz"], entrada["originales"])
    generar_graficos_metodos(entrada, {"kmeans": resultado}, Path(directorio))
    imprimir_resultado("kmeans", resultado)
    return {
        "resultado": resultado,
        "casos": [
            {
                "nombre": "referencia",
                "descripcion": "K-Means k=7",
                "resultado": resultado,
            }
        ],
    }
