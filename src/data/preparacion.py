"""Prepara las variables y conserva la estandarización del análisis original."""

import numpy as np


def preparar_variables(alumnos):
    """Convierte tiempos a días y selecciona las variables, sin modificar la entrada."""
    # Preparación de variables para el análisis

    # Removemos la información que no es necesario del dataframe para analizar y poner la información en el formato correcto
    # Limpieza y selección de variables relevantes
    # Objetivo: preparar los datos solo con las variables numéricas necesarias para hacer clustering.
    alumnos_s_avanzados = alumnos.copy()
    alumnos_s_avanzados["tiempo_desde_ingreso"] = (
        alumnos_s_avanzados["tiempo_desde_ingreso"].dt.total_seconds() / 86400
    )
    alumnos_s_avanzados["deserto"] = alumnos_s_avanzados["deserto"].astype(float)
    alumnos_s_avanzados["dias_dsd_ultimo_final"] = (
        alumnos_s_avanzados["dias_dsd_ultimo_final"].dt.total_seconds() / 86400
    )

    # Eliminamos variables que no nos interesan para el análisis

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
    """Estandariza con desvío muestral y calcula las correlaciones originales.

    Incluye deserto, como en la entrada original. Las etiquetas de clustering
    se agregan después de este paso.
    """
    alumnos_s_avanzados_sc = (
        alumnos_s_avanzados - alumnos_s_avanzados.mean(axis=0)
    ) / alumnos_s_avanzados.std(axis=0, ddof=1)
    matriz_cor = alumnos_s_avanzados_sc.corr()  # noqa: F841 — conserva el cálculo exploratorio
    matriz_cor_comparacion = alumnos_s_avanzados.corr()  # noqa: F841 — conserva el cálculo exploratorio
    alumnos_s_avanzados_sc.index = np.arange(1, len(alumnos_s_avanzados_sc) + 1)

    return alumnos_s_avanzados_sc
