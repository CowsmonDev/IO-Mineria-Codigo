"""Ejecución de la referencia jerárquica y generación de sus salidas."""

from pathlib import Path

from src.methods import jerarquico
from src.runs._salidas import imprimir_resultado
from src.runs.visualizacion.visualizacion import generar_graficos_metodos


def pruebas(entrada, directorio):
    """Ejecuta la referencia fija sobre la entrada común y guarda sus salidas."""
    resultado = jerarquico.analizar(entrada["matriz"], entrada["originales"])
    directorio = Path(directorio)
    generar_graficos_metodos(entrada, {"jerarquico": resultado}, directorio)
    guardar_resumen(resultado, directorio / "jerarquico")
    imprimir_resultado("jerarquico", resultado)
    return {
        "resultado": resultado,
        "casos": [
            {
                "nombre": "referencia",
                "descripcion": "Referencia Ward h=35",
                "resultado": resultado,
            }
        ],
    }


def guardar_resumen(resultado, directorio):
    """Guarda el único CSV del jerárquico con las columnas del resumen original R."""
    columnas = {
        "cantidad": "cantidad_observaciones",
        "cursadas_aprobadas": "media_cursadas_aprobadas",
        "cursadas_desaprobadas": "media_cursadas_desaprobadas",
        "materias_anotado_ult_anio": "media_materias_anotado_ult_anio",
        "finales_aprobados": "media_finales_aprobados",
        "finales_desaprobados": "media_finales_desaprobados",
        "cursadas_promocionadas": "media_cursadas_promocionadas",
        "porc_finales": "media_porc_finales",
        "tiempo_desde_ingreso": "media_T_desde_ingreso",
        "deserto": "media_deserto",
        "dias_dsd_ultimo_final": "media_dias_dsd_ultimo_final",
    }
    # Conservar también el uso con entradas sintéticas de las pruebas.
    resumen = resultado["resumen"]
    columnas_presentes = [col for col in columnas if col in resumen]
    tabla = (
        resumen[columnas_presentes]
        .rename(columns=columnas)
        .rename_axis("cluster")
        .reset_index()
    )
    directorio.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(directorio / "resumen_clusters.csv", index=False)
