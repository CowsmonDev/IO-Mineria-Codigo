"""Columnas de la entrada de clustering, en el orden utilizado por el análisis."""

from typing import TypedDict

import numpy as np
import pandera.pandas as pa
from pandera.typing import DataFrame, Series


class VariablesOriginales(pa.DataFrameModel):
    """Indicadores sin estandarizar; los conteos se almacenan como float64."""

    tiempo_desde_ingreso: Series[float] = pa.Field(description="Días desde el ingreso.")
    cursadas_aprobadas: Series[float] = pa.Field(
        description="Cantidad de cursadas aprobadas."
    )
    cursadas_promocionadas: Series[float] = pa.Field(
        description="Cantidad de cursadas promocionadas."
    )
    cursadas_desaprobadas: Series[float] = pa.Field(
        description="Cantidad de cursadas desaprobadas."
    )
    materias_anotado_ult_anio: Series[float] = pa.Field(
        description="Materias distintas con inscripción en el último año."
    )
    finales_aprobados: Series[float] = pa.Field(
        description="Cantidad de finales aprobados."
    )
    finales_desaprobados: Series[float] = pa.Field(
        description="Cantidad de finales desaprobados."
    )
    dias_dsd_ultimo_final: Series[float] = pa.Field(
        description="Días desde el último final; sin finales, desde el ingreso."
    )
    porc_finales: Series[float] = pa.Field(
        description="Finales aprobados divididos por la cantidad de materias del plan."
    )
    deserto: Series[float] = pa.Field(
        isin=[0.0, 1.0], description="Indicador de deserción: 0 o 1."
    )

    class Config:
        strict = True
        ordered = True


class VariablesEstandarizadas(pa.DataFrameModel):
    """Mismas columnas, con media cero y desvío muestral uno (ddof=1).

    Todas las variables, incluido deserto, contienen valores estandarizados.
    La correspondencia con los originales se comprueba en validar_entrada.
    """

    tiempo_desde_ingreso: Series[float]
    cursadas_aprobadas: Series[float]
    cursadas_promocionadas: Series[float]
    cursadas_desaprobadas: Series[float]
    materias_anotado_ult_anio: Series[float]
    finales_aprobados: Series[float]
    finales_desaprobados: Series[float]
    dias_dsd_ultimo_final: Series[float]
    porc_finales: Series[float]
    deserto: Series[float]

    class Config:
        strict = True
        ordered = True


class EntradaClustering(TypedDict):
    """Tablas e identificadores alineados por posición, no por índice de pandas."""

    originales: DataFrame[VariablesOriginales]
    matriz: DataFrame[VariablesEstandarizadas]
    ids_alumnos: np.ndarray
    fecha_analisis: str
