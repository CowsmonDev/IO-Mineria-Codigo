"""Campos que los conjuntos de gráficos consumen de los resultados en memoria.

Estos contratos describen la parte utilizada por visualización; los métodos
pueden devolver otros campos. No reemplazan la validación de datos con Pandera.
"""

from typing import NotRequired, TypedDict

import numpy as np
import pandas as pd
from numpy.typing import NDArray


class ParametrosVisualizacion(TypedDict, total=False):
    """Parámetros necesarios para rotular diagnósticos específicos."""

    height: float
    eps: float
    min_samples: int


class ResultadoVisualizacion(TypedDict):
    """Resultado común con diagnósticos opcionales según el algoritmo."""

    etiquetas: NDArray[np.integer]
    resumen: pd.DataFrame
    silhouette: NDArray[np.float64]
    motivo_silhouette: str
    parametros: ParametrosVisualizacion
    enlace: NotRequired[NDArray[np.float64]]
    silhouette_por_k: NotRequired[pd.Series]
    distancias_vecinos: NotRequired[NDArray[np.float64]]
    ruido: NotRequired[int]
    grupos: NotRequired[int]


class CasoVisualizacion(TypedDict):
    """Una configuración identificada para generar y comparar sus salidas."""

    nombre: str
    descripcion: str
    resultado: ResultadoVisualizacion
