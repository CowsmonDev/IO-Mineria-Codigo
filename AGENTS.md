# Indicaciones para trabajar en este repositorio

## Tipado de Python

- Agregar anotaciones de parámetros y retorno a las funciones nuevas o modificadas. Aplicar el tipado de forma incremental en los módulos que se están trabajando.
- Usar tipos concretos cuando se conocen: `matplotlib.figure.Figure` para figuras, `pd.DataFrame` y `pd.Series` para tablas y series, `str | Path` para rutas y `None` para funciones sin retorno.
- Las funciones `graficar_*` deben devolver `Figure`. `guardar_figura` debe recibir `Figure` y devolver `None`; las funciones que arman conjuntos de salida también devuelven `None`.
- Reutilizar los contratos existentes, como `EntradaClustering`. Para diccionarios con una estructura conocida, preferir `TypedDict` con campos explícitos y marcar los opcionales con `NotRequired`, en lugar de recurrir a `dict` sin parámetros o a `Any`.
- Usar `ArrayLike` para entradas numéricas que admiten listas, arrays o series y `NDArray` cuando el contrato exige un array NumPy. Usar `Sequence` o `Mapping` para colecciones que sólo se leen.
- Las anotaciones documentan contratos y ayudan al editor; no sustituyen las validaciones necesarias en tiempo de ejecución ni la validación de datos con Pandera.

## Nombres de archivos

- Usar `esquemas.py` para los contratos de estructura de datos de cada módulo, tanto los definidos con `TypedDict` como los que incluyen validación con Pandera. Aclarar en la documentación si el contrato valida datos en ejecución o sólo aporta tipado.

## Verificación

- Ejecutar `uv run ruff check main.py src tests` y las pruebas pertinentes con `uv run pytest -q` después de cambios en Python. Si el entorno `.venv` ya está preparado, se pueden usar sus ejecutables directamente.
