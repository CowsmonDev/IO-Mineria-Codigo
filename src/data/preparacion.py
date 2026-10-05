"""Prepara las variables y conserva la estandarización del análisis original."""

import numpy as np
import pandas as pd


def preparar_variables(alumnos):
    """Convierte tiempos a días y selecciona las variables, sin modificar la entrada."""
    alumnos_s_avanzados = alumnos.copy()
    alumnos_s_avanzados["tiempo_desde_ingreso"] = (
        alumnos_s_avanzados["tiempo_desde_ingreso"].dt.total_seconds() / 86400
    )
    alumnos_s_avanzados["deserto"] = alumnos_s_avanzados["deserto"].astype(float)
    alumnos_s_avanzados["dias_dsd_ultimo_final"] = (
        alumnos_s_avanzados["dias_dsd_ultimo_final"].dt.total_seconds() / 86400
    )

    alumnos_s_avanzados = alumnos_s_avanzados.drop(
        columns=[
            "nota_finales_ult_anio",
            "cursadas_regulares",
            "notas_cursadas_ult_anio",
            "relacion_finales_cursadas",
            "porc_cursadas",
            "total_materias_finalizadas",
            "localidad_nacimiento",
            "fecha_inscripcion",
            "cambio_plan",
            "id_alumno",
            "plan",
            "carrera",
            "calidad",
        ]
    )

    return alumnos_s_avanzados


def estandarizar(alumnos_s_avanzados):
    """Estandariza con desvío muestral, conservando las variables originales.

    Incluye deserto, como en la entrada original. Las etiquetas de clustering
    se agregan después de este paso.
    """
    alumnos_s_avanzados_sc = (
        alumnos_s_avanzados - alumnos_s_avanzados.mean(axis=0)
    ) / alumnos_s_avanzados.std(axis=0, ddof=1)
    alumnos_s_avanzados_sc.index = np.arange(1, len(alumnos_s_avanzados_sc) + 1)

    return alumnos_s_avanzados_sc


def preparar_entrada(datos):
    """Conserva identidad, unidades originales y matriz común sin etiquetas."""
    alumnos = datos["alumnos_s_avanzados"]
    originales = preparar_variables(alumnos).reset_index(drop=True)
    entrada = {
        "originales": originales,
        "matriz": estandarizar(originales),
        "ids_alumnos": alumnos["id_alumno"].to_numpy(copy=True),
        "fecha_analisis": datos["fecha_analisis"],
    }
    validar_entrada(entrada)
    return entrada


def validar_entrada(entrada):
    """Rechaza contaminación por etiquetas, identidades inválidas y desalineación."""
    originales, matriz = entrada["originales"], entrada["matriz"]
    ids = np.asarray(entrada["ids_alumnos"])
    if any(str(col).startswith("cluster") for col in matriz.columns):
        raise ValueError("Las etiquetas de clustering no pueden integrar la entrada.")
    if list(originales.columns) != list(matriz.columns):
        raise ValueError("Las variables originales y estandarizadas no coinciden.")
    if len(originales) != len(matriz) or len(ids) != len(matriz):
        raise ValueError("Las tablas y los identificadores deben tener igual longitud.")
    if pd.isna(ids).any() or pd.Series(ids).duplicated().any():
        raise ValueError("Cada fila debe tener un id_alumno único y no nulo.")
    if not np.isfinite(matriz.to_numpy(dtype=float)).all():
        raise ValueError("La entrada contiene valores faltantes o no finitos.")
    esperada = (originales - originales.mean()) / originales.std(ddof=1)
    if not np.allclose(matriz.to_numpy(), esperada.to_numpy(), rtol=1e-10, atol=1e-10):
        raise ValueError(
            "La entrada no conserva el orden y la estandarización original."
        )
