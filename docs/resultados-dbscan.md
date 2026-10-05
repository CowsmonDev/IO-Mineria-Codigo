# Ejecución básica de DBSCAN

Estado actual: implementación e inspección de grupos y gráficos, antes de la comparación sistemática.

## Configuración inicial

Se utiliza la entrada común de 2.587 estudiantes y diez variables, con fecha de análisis `2026-10-01`. Los parámetros iniciales retoman el antecedente original: `eps=1.5`, `min_samples=5`, distancia euclídea. Se ejecuta una sola configuración; no se seleccionan parámetros automáticamente.

## Resultado observado

La ejecución inicial produjo un grupo de 2.393 estudiantes y 194 casos de ruido (7,4990% de la población). El resumen muestra cantidades y medias en unidades originales, incluyendo el ruido como categoría `-1`.

Silhouette excluye ruido y no se puede calcular con un único grupo. El programa informa ese motivo y continúa generando los gráficos. Esto es un resultado válido de la configuración utilizada; corresponde inspeccionar el gráfico de vecinos y probar otros parámetros de forma explícita antes de definir una configuración para comparar.

La entrada conserva `deserto`, como en la referencia original. Sus diferencias entre grupos no constituyen validación independiente de la deserción.

## Ejecución e inspección

```bash
uv run python main.py
```

Los resultados básicos se muestran en consola y los PNG se guardan en `output/<método>/graficos/`. Para probar otros parámetros y conservar sus gráficos en otra carpeta:

```bash
uv run python main.py --eps 0.8 --min-samples 10 --salida output/experimentos/dbscan_0_8_10
```

Los gráficos disponibles incluyen distancias a vecinos de DBSCAN, tamaños, perfiles y Silhouette cuando corresponde. No se exportan tablas ni se calculan ARI, correspondencias o estabilidad entre configuraciones.

Referencia: [DBSCAN en scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html). `min_samples` incluye al propio punto; para cinco se representa la distancia al cuarto vecino externo.
