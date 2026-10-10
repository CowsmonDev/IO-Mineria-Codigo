# Comparación de agrupamientos de estudiantes

Trabajo final de Investigación Operativa — Facultad de Ciencias Exactas, UNICEN.

El proyecto estudia **cómo cambia la agrupación de los mismos estudiantes al aplicar K-Means y DBSCAN sobre los mismos atributos utilizados por el clustering jerárquico del estudio de Clementi y Salias**. Se compararán la cantidad de grupos, sus integrantes y sus características académicas para interpretar qué perfiles se conservan, se dividen, se fusionan o quedan como ruido.

Cada método recibe la misma matriz estandarizada y produce su propia asignación de alumnos. K-Means y DBSCAN se ejecutan directamente sobre los atributos; no reciben los grupos jerárquicos como entrada. La segmentación jerárquica sirve como referencia de comparación, sin tratarla como una clasificación verdadera.

La propuesta retoma la línea de trabajos futuros del informe dedicada a contrastar los perfiles mediante otros algoritmos de clustering. En esta etapa se usan los datos académicos existentes; el enriquecimiento socioeconómico y la predicción supervisada son otras líneas de continuidad.

## Estado actual

Los tres métodos están implementados y generan resúmenes y gráficos individuales. Para la fecha de análisis `2026-10-01`, la entrada contiene 2.587 alumnos y diez atributos:

| Método | Configuración actual | Grupos | Ruido | Silhouette |
|---|---|---:|---:|---:|
| Jerárquico | Euclídea, Ward, corte h=35 | 7 | 0 | 0,295444 |
| K-Means | k=7, 25 inicializaciones, semilla 123 | 7 | 0 | 0,365474 |
| DBSCAN | eps=1,5; min_samples=5 | 1 | 194 (7,5 %) | No calculable: un grupo sin ruido |

Los siete grupos de K-Means son una decisión de la configuración actual. Sus integrantes pueden diferir de los del jerárquico. En DBSCAN, la cantidad de grupos surge de la densidad; no se exige que sean siete.

La migración jerárquica R–Python está verificada: con los mismos CSV y la misma fecha, ambas implementaciones seleccionan los mismos alumnos y atributos y producen el mismo agrupamiento y Silhouette dentro de la precisión numérica. Se comprobó en cinco fechas; ver [verificación R–Python](docs/resultados/verificacion-fechas-r-python.md).

El requisito del proyecto es esa equivalencia entre implementaciones. Reproducir las cifras, figuras o fecha exacta del PDF no es un requisito ni una tarea pendiente. La entrada de trabajo conserva la fecha `2026-10-01`. Se realizaron exploraciones locales de DBSCAN; la comparación completa de perfiles entre los tres métodos sigue pendiente. La [búsqueda de siete grupos con poco ruido](docs/resultados/concordancia-dbscan.md) obtuvo esa cantidad, pero mantuvo una gran concentración y poca concordancia con el jerárquico. No se seleccionó una nueva configuración predeterminada.

## Ejecución

Se utiliza Python 3.11 y uv. Los datos deben estar disponibles localmente en `data/`:

- `001_alumnos.csv`
- `002_regularidades.csv`
- `003_historia_academica.csv`
- `000_materias_planes.csv`

```bash
uv sync
uv run python main.py
```

La fecha predeterminada es `2026-10-01`, usada para la ejecución reproducible actual. `--fecha` tiene prioridad sobre `ANALYSIS_DATE` y permite cambiarla:

```bash
uv run python main.py --fecha 2026-10-01
```

Cambiar la fecha puede cambiar los indicadores y las asignaciones. El indicador de actividad llamado «último año» sigue referido a 2023, conforme al procesamiento heredado; no se desplaza con `--fecha`.

DBSCAN recibe parámetros explícitos. Por ejemplo, para explorar otra configuración y conservar sus salidas:

```bash
uv run python main.py --eps 0.8 --min-samples 10 --salida output/dbscan/experimentos/dbscan_0_8_10
```

Este comando ejecuta los tres métodos y los cinco casos fijos de DBSCAN, y guarda sus resultados en la raíz indicada. `--eps` y `--min-samples` modifican la ejecución individual de DBSCAN; los casos fijos conservan sus parámetros. Los valores del ejemplo son exploratorios, no una configuración final seleccionada. `min_samples` incluye al propio alumno.

## Entrada y resultado

`main.py` llama a `preparar_entrada(fecha_analisis=fecha)`. Esa función carga los datos mediante `manipulacion.preparar_datos_academicos`, conserva los identificadores y prepara los valores originales y la matriz estandarizada con desvío muestral (`ddof=1`). Pandera valida las columnas, su orden, tipos y ausencia de nulos; también se verifica la alineación de los alumnos.

Las diez variables y su significado se describen en [el informe](docs/referencias/informe.md#3-entrada-común). Los identificadores y etiquetas de clusters quedan fuera de la matriz. Se conserva `deserto` como atributo, siguiendo el código original; sus porcentajes por grupo son descriptivos y no validan una predicción de abandono.

Cada algoritmo devuelve:

- Una etiqueta por alumno; DBSCAN utiliza `-1` para ruido.
- Una tabla de cantidades y medias en unidades originales por grupo.
- Silhouette individual y promedio cuando se puede calcular.
- Información propia del método: árbol jerárquico, centros e inercia de K-Means, o ruido y distancias de vecinos de DBSCAN.

Las etiquetas numéricas son independientes: el grupo 1 de un método no necesariamente corresponde al grupo 1 de otro. Los resultados quedan en memoria al llamar a `main()` desde Python; los parámetros, resúmenes y Silhouette se muestran en consola. Además de `entrada` y `resultados`, el retorno contiene `pruebas_dbscan`: una lista de casos con `nombre`, `descripcion` y `resultado`. Cada resultado conserva la estructura que devuelve `dbscan.analizar`.

## Salidas en disco

```text
output/
├── jerarquico/
│   ├── resumen_clusters.csv
│   └── graficos/              # PNG y PDF de dendrogramas internos y zooms
├── k-means/
│   └── graficos/              # PNG
└── dbscan/
    ├── graficos/              # PNG, incluido vecinos.png
    └── experimentos/          # Cinco casos fijos de main y pruebas locales
        ├── <caso>/graficos/    # Figuras individuales de DBSCAN
        └── graficos/          # Comparación de grupos, ruido y concentración
```

Se generan tamaños, Silhouette, boxplots de finales aprobados y promocionadas y proporción de deserción. Si Silhouette no está disponible, su figura explica el motivo.

El jerárquico también genera el dendrograma general, Silhouette para k=2 a 15, dendrogramas internos con cuatro subgrupos y zooms de los primeros 50 casos para grupos de al menos 500 alumnos. Los zooms son dendrogramas recalculados sobre esos casos; no representan necesariamente todo el grupo. Se agregan gráficos de deserción individual y avance frente a promocionadas. La curva de Silhouette no modifica el corte h=35.

Actualmente se guarda un CSV para el jerárquico y gráficos por método. La ejecución recalcula cinco casos fijos de DBSCAN sobre la misma entrada y muestra una tabla de grupos, ruido, concentración y Silhouette. Genera gráficos individuales por caso y una figura conjunta en `output/dbscan/experimentos/graficos/comparacion.png`. No realiza una búsqueda de parámetros ni selecciona automáticamente un ganador. Las exploraciones históricas y el diagnóstico sin `deserto` no se ejecutan desde `main`. `data/` y `output/` están excluidos de Git.

## Organización y verificación

```text
main.py                         # Coordina preparación, algoritmos y gráficos
src/
├── data/
│   ├── manipulacion.py         # CSV, filtros e indicadores académicos
│   ├── esquemas.py             # Columnas y tipos de los DataFrames (Pandera)
│   └── preparacion.py          # Carga, identidad y estandarización
├── clustering/
│   ├── jerarquico.py           # Árbol Ward y corte h=35
│   ├── kmeans.py               # Agrupamiento alrededor de centros
│   └── dbscan.py               # Agrupamiento por densidad y ruido
├── visualizacion.py           # Gráficos individuales
└── lasso.py                   # Antecedente independiente
```

```bash
uv run pytest -q
uv run ruff check main.py src tests
```

LASSO toma los valores originales de la misma preparación y puede ejecutarse por separado:

```bash
ANALYSIS_DATE=2026-10-01 uv run --group antecedentes python -m src.lasso
```

Sus coeficientes no seleccionan ni ponderan las variables del clustering. Los scripts R y notebooks de la migración se conservan en `Legacy/`.

La [guía de documentación](docs/README.md) reúne el alcance, el borrador de informe, las ejecuciones registradas, el flujo por archivos y los PDF de referencia.
