# Clustering para la segmentación de estudiantes

Trabajo final de Investigación Operativa — Facultad de Ciencias Exactas, UNICEN.

En esta etapa se implementan jerárquico, K-Means y DBSCAN sobre la misma entrada preparada, para inspeccionar sus grupos y gráficos. La comparación sistemática entre métodos queda para una etapa posterior.

## Ejecución

Se utiliza Python 3.11 y uv:

```bash
uv sync
uv run python main.py
```

La preparación se ejecuta una sola vez. La fecha predeterminada es `2026-10-01`, correspondiente a la referencia verificada de la migración. `--fecha` permite cambiarla y tiene prioridad sobre `ANALYSIS_DATE`:

```bash
uv run python main.py --fecha 2026-10-01
```

DBSCAN ejecuta una configuración explícita, inicialmente `eps=1.5` y `min_samples=5`, retomando el antecedente original. Se pueden cambiar uno o ambos parámetros y guardar los gráficos en otra carpeta:

```bash
uv run python main.py --eps 0.8 --min-samples 10 --salida output/experimentos/dbscan_0_8_10
```

Los parámetros no se seleccionan automáticamente. `min_samples` incluye al propio punto. Cambiar la fecha puede modificar los indicadores y las asignaciones; para conservar la entrada de referencia se debe usar `2026-10-01`.

## Organización

```text
main.py                         # Preparación, algoritmos y gráficos
src/
├── data/
│   ├── manipulacion.py         # CSV, filtros e indicadores originales
│   ├── esquemas.py             # Columnas, tipos y significado de la entrada (Pandera)
│   └── preparacion.py          # Variables, identidad y estandarización
├── clustering/
│   ├── jerarquico.py           # Ward, Silhouette y resumen por grupo
│   ├── kmeans.py               # K-Means, Silhouette y resumen por grupo
│   └── dbscan.py               # DBSCAN, ruido, Silhouette y vecinos
├── visualizacion.py            # Gráficos para inspeccionar los resultados
└── lasso.py                    # Antecedente independiente
```

Los CSV requeridos en `data/` son `001_alumnos.csv`, `002_regularidades.csv`, `003_historia_academica.csv` y `000_materias_planes.csv`. Las rutas de entrada se resuelven desde el proyecto.

La entrada verificada contiene 2.587 estudiantes y diez variables, estandarizadas con desvío muestral (`ddof=1`). Los identificadores y etiquetas de grupos quedan fuera de la matriz. Se conserva `deserto`, como en el estudio original: su distribución entre grupos es descriptiva y no constituye validación independiente de la deserción.

Los esquemas `VariablesOriginales` y `VariablesEstandarizadas`, en `src/data/esquemas.py`, declaran las diez columnas en su orden esperado y sus tipos. Los originales conservan días, conteos y proporciones; los conteos también se almacenan como `float64`. En ellos, `deserto` solo admite 0 o 1; en la matriz está estandarizado. Pandera valida columnas, orden, tipos y ausencia de nulos al preparar la entrada. Las tablas y los identificadores se corresponden por posición (`iloc`), aunque sus índices sean distintos.

## Resultados básicos

- **Jerárquico:** distancia euclídea, Ward y corte a altura 35. Se exige que reproduzca los siete grupos de referencia.
- **K-Means:** siete grupos, k-means++, 25 inicializaciones, semilla 123 y Lloyd. Se conserva la menor inercia entre esas inicializaciones. Se ejecuta una sola corrida; no se realizan repeticiones adicionales para evaluar estabilidad.
- **DBSCAN:** una corrida con los parámetros indicados. Los grupos tienen etiquetas desde 1 y el ruido conserva `-1`. Silhouette excluye ruido y se informa la cantidad efectivamente evaluada. Si no hay entre dos y `n-1` grupos evaluables, se informa el motivo y la ejecución continúa.

Cada algoritmo devuelve sus asignaciones, Silhouette y un resumen con cantidades y medias en unidades originales. Se muestran parámetros, resúmenes y Silhouette en consola. Los resultados también quedan disponibles en memoria al llamar a `main()` desde Python.

## Gráficos y salidas

Los PNG se guardan por dominio: `output/jerarquico/graficos/`, `output/dbscan/graficos/` y `output/k-means/graficos/`. `--salida` cambia la raíz de resultados; dentro de ella se crean esas tres carpetas de dominio y sus respectivas carpetas `graficos/`. Se generan tamaños de grupos, Silhouette, perfiles de finales aprobados y cursadas promocionadas, proporción de deserción, distancias a vecinos de DBSCAN y dendrogramas generales e internos.

Cada gráfico corresponde a un solo método y se guarda en su carpeta de dominio. Los números de grupos son etiquetas independientes y no implican correspondencia entre métodos.

El jerárquico recupera las salidas del original R: `resumen_clusters.csv` en su carpeta de dominio; dendrogramas internos con cuatro subgrupos y zooms de los primeros 50 casos para grupos de al menos 500 estudiantes, en PDF y PNG dentro de `graficos/`. También se generan Silhouette para k=2 a 15, distribución individual de deserción y avance frente a promocionadas. Este diagnóstico de k no modifica el corte fijo a altura 35.

K-Means y DBSCAN generan únicamente PNG; no se genera JSON. ARI, correspondencias, análisis de estabilidad, exploraciones automáticas y exportaciones masivas quedan para cuando se aborde la comparación. Las salidas de experimentos previos, si existen, no se actualizan con este comando. Los datos y `output/` están excluidos de Git.

## Verificación y antecedentes

```bash
uv run pytest -q
uv run ruff check main.py src tests
```

Las pruebas cubren identidad y orden de la entrada, agrupamientos, ruido, vecindades, particiones sin Silhouette y generación de gráficos y el resumen CSV original del jerárquico.

LASSO puede ejecutarse por separado con su dependencia opcional:

```bash
ANALYSIS_DATE=2026-10-01 uv run --group antecedentes python -m src.lasso
```

Los scripts R y notebooks migrados se conservan en `Legacy/`. Los antiguos coordinadores `analisis_preliminar.py` y `analisis_extra.py` fueron eliminados del código activo. PAM, Random Forest y las ejecuciones duplicadas de K-Means quedan en el histórico.

La documentación del trabajo se mantiene en `docs/`: [criterios acordados](docs/criterios-del-trabajo.md), [informe](docs/informe.md), [primera ejecución K-Means](docs/resultados-kmeans.md), [ejecución básica DBSCAN](docs/resultados-dbscan.md) y [flujo por archivos](docs/flujo-archivos.md).
