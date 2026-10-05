# Objetivos y alcance del final de Investigación Operativa

## Comparación de técnicas de clustering aplicadas a la segmentación de estudiantes

**Facultad de Ciencias Exactas UNICEN | Proyecto IO Minería | Septiembre de 2026**

Este documento establece el propósito, el alcance inicial y el criterio metodológico del trabajo final. El estudio evaluará cómo cambia la segmentación de estudiantes cuando el problema abordado por Clementi y Salias mediante clustering jerárquico se analiza con una técnica alternativa. La comparación conservará la intención y las condiciones centrales del análisis original, y su extensión definitiva se resolverá a partir de la complejidad y de los resultados obtenidos.

## Entorno de desarrollo Python

El proyecto utiliza Python 3.11 y [uv](https://docs.astral.sh/uv/) para gestionar el entorno virtual y las dependencias. Para crear o sincronizar el entorno local:

```powershell
uv sync
```

Los comandos del proyecto se ejecutan dentro del entorno administrado por uv, sin necesidad de activarlo manualmente. Por ejemplo:

```powershell
uv run python --version
uv run pytest
```

Para trabajar con PyCharm, se debe abrir este directorio como proyecto y seleccionar como intérprete el ejecutable `.venv\Scripts\python.exe`. Las dependencias de ejecución y desarrollo están declaradas en `pyproject.toml`. El directorio `.venv` es local y descartable; no debe incorporarse al control de versiones.

## Análisis en scripts Python

Para ejecutar las tres etapas en secuencia desde la raíz del proyecto:

```bash
uv run python main.py
```

El punto de entrada `main.py` importa las tres etapas y las ejecuta en el mismo proceso, en orden. Cada etapa devuelve un diccionario con los datos que necesita la siguiente. Si una falla, la ejecución se detiene. El progreso y las carpetas de salida se informan en la consola.

También se pueden ejecutar los módulos desde la raíz del proyecto:

```bash
uv run python -m src.data.manipulacion
uv run python -m src.analisis_preliminar
uv run python -m src.analisis_extra
```

Al ejecutar el análisis preliminar por separado, este importa y ejecuta primero la preparación de datos. Al ejecutar el análisis extra, se ejecutan antes ambas etapas anteriores. Para correr todo una sola vez, usar `main.py`.

El código se organiza así:

```text
main.py
src/
├── data/
│   ├── manipulacion.py       # CSV, filtros de población e indicadores
│   └── preparacion.py        # Variables en unidades originales y estandarización
├── clustering/
│   └── jerarquico.py         # Ward, dendrogramas, resumen y Silhouette
├── lasso.py                  # Regresión logística y coeficientes originales
├── analisis_preliminar.py    # Coordinación y gráficos descriptivos
└── analisis_extra.py         # Hopkins, K-Means, DBSCAN, PAM y Random Forest
```

La carpeta `data/` de la raíz conserva los CSV de entrada; `src/data/` contiene el código que los prepara. `analisis_preliminar.main()` coordina la preparación de variables, LASSO y el jerárquico, y devuelve el mismo diccionario que consume el análisis extra. La preparación mantiene las variables originales, incluida `deserto`, y estandariza con desvío muestral (`ddof=1`) antes de agregar las etiquetas de grupos. LASSO utiliza la tabla en unidades originales y sus coeficientes no seleccionan ni ponderan las variables del clustering.

Importar los módulos no inicia el análisis: las etapas se ejecutan al llamar a `main()`. Los datos se pasan en memoria; no se guardan ni se cargan archivos intermedios. Esta reorganización conserva los parámetros, cálculos y salidas existentes; el análisis extra permanece sin cambios.

Para reproducir una ejecución con una fecha de análisis fija, se puede definir `ANALYSIS_DATE`. Si no se define, la preparación usa el día de ejecución:

```bash
ANALYSIS_DATE=2026-10-01 uv run python main.py
```

Los gráficos se exportan como PNG en `output/graficos/02_analisis_preliminar/` y `output/graficos/03_analisis_extra/`. El análisis preliminar genera 16 PNG con los datos actuales: siete gráficos generales, siete dendrogramas individuales y dos zooms. Los dendrogramas conservan además sus PDF en `output/dendrogramas/`. Los scripts generan los archivos sin abrir ventanas y al finalizar muestran en la consola las rutas completas de las carpetas donde se guardaron.

El análisis extra conserva su implementación actual y las diferencias conocidas respecto de R. Silhouette de DBSCAN se omite si, al excluir el ruido, no hay entre dos y `n - 1` grupos; el script informa el motivo y continúa hasta Random Forest.

Los archivos de `output/` contienen datos estudiantiles y están excluidos de Git. Los scripts de `src/` son la fuente activa del análisis en Python. Las copias completas de los notebooks anteriores se conservan en `Legacy/migracion_inicial/`, con sus comentarios y salidas, para mantener la historia de la migración.

## Antecedentes y origen

El informe de Clementi y Salias estudió la deserción en Ingeniería de Sistemas de la Facultad de Ciencias Exactas de la UNICEN a partir de datos académicos del sistema SIU Guaraní. Para segmentar trayectorias estudiantiles aplicó clustering jerárquico aglomerativo con distancia euclídea y enlace `ward.D2`. El número de grupos se definió mediante el índice Silhouette y el análisis resultante tomó siete clústeres como base para caracterizar perfiles de estudiantes.

En la sección de trabajos futuros, ese informe propuso aplicar K-Means y DBSCAN para contrastar la estabilidad de los perfiles. Posteriormente, un revisor del artículo derivado del trabajo solicitó una comparación empírica con esos algoritmos y una discusión de las diferencias de segmentación. En la reunión del 17 de septiembre de 2026, el profesor Gustavo Illescas indicó que esa observación constituye el punto de partida del final.

## Objetivo general

Comparar empíricamente la segmentación obtenida mediante clustering jerárquico con la producida por una o más técnicas alternativas, inicialmente K-Means y/o DBSCAN, para determinar en qué medida se conservan o cambian los perfiles estudiantiles vinculados con la deserción.

## Objetivos específicos

1. Establecer como referencia la configuración, las variables y los perfiles obtenidos mediante clustering jerárquico en el trabajo de Clementi y Salias.
2. Implementar inicialmente una técnica alternativa de agrupamiento y documentar las decisiones de preparación de datos y parametrización que requiera.
3. Evaluar cada segmentación con criterios comparables de cohesión, separación, tamaño de los grupos, estabilidad e interpretabilidad de los perfiles.
4. Identificar similitudes y diferencias en la asignación de estudiantes y en las características académicas que describen a cada grupo.
5. Determinar, a partir de la primera comparación, si corresponde incorporar un segundo algoritmo o acotar el estudio a un análisis introductorio técnicamente justificado.

## Alcance inicial

La primera etapa comprenderá la reproducción o verificación del resultado de referencia y la aplicación de un algoritmo alternativo sobre el mismo problema de segmentación. K-Means es una opción natural para una comparación basada en particiones; DBSCAN permite explorar agrupamientos por densidad e identificar ruido. La selección inicial entre ambas técnicas deberá considerar las características del conjunto de datos y la posibilidad de establecer una comparación metodológicamente válida.

No se plantea como objetivo inicial rehacer todo el estudio previo, incorporar nuevas fuentes de datos, desarrollar un modelo predictivo supervisado ni revisar de manera general las conclusiones causales del informe. Esas líneas podrán considerarse únicamente si los resultados muestran que son necesarias para interpretar la comparación.

## Metodología comparativa esperada

La comparación debe mantener constantes los elementos que definen el problema y explicitar cualquier cambio exigido por el algoritmo alternativo. Los grupos no se compararán solo por su numeración, sino por su composición y por los perfiles académicos que representan.

| Elemento | Criterio de comparación |
|---|---|
| **Población y datos** | Usar el mismo universo de estudiantes y los mismos criterios de inclusión del análisis de referencia. |
| **Variables** | Conservar las variables académicas y el tratamiento previo. Justificar normalización, selección o transformación adicional. |
| **Método de referencia** | Clustering jerárquico aglomerativo con distancia euclídea, enlace `ward.D2` y siete grupos seleccionados mediante Silhouette. |
| **Método alternativo** | Aplicar K-Means o DBSCAN. Documentar la elección de `k` o de los parámetros de densidad y el tratamiento de observaciones consideradas ruido. |
| **Evaluación** | Comparar validez interna, tamaños de grupos, estabilidad, correspondencia de asignaciones e interpretabilidad de los perfiles. |
| **Interpretación** | Describir qué perfiles se mantienen, cuáles se dividen o se fusionan y qué estudiantes cambian de agrupamiento. |

## Criterio de continuidad

El análisis conservará el mismo hilo del trabajo original. Esto implica estudiar la segmentación de los estudiantes con la misma intención descriptiva y diagnóstica, sobre variables equivalentes y con criterios de interpretación compatibles. El foco estará en el efecto del cambio de técnica sobre los agrupamientos. Las diferencias respecto de las conclusiones previas se registrarán cuando surjan de la comparación, pero no serán el punto de partida del estudio.

## Ajuste del alcance final

El alcance definitivo se decidirá después de obtener los primeros resultados. Si una sola técnica alternativa produce una comparación suficientemente compleja, el trabajo podrá concentrarse en ella. Si el análisis resulta breve o poco informativo, se incorporará una segunda técnica. Si la implementación o la interpretación exceden el tiempo disponible, se delimitará un estudio introductorio que documente con claridad sus decisiones y limitaciones. Los ajustes se acordarán con el profesor a partir de resultados intermedios.

## Resultado esperado

El producto final deberá presentar una comparación reproducible de las técnicas, acompañada por métricas, tablas o gráficos que permitan evaluar la calidad de los agrupamientos y por una interpretación de los perfiles obtenidos. La conclusión deberá indicar qué aspectos de la segmentación original se mantienen, cuáles cambian y qué limitaciones condicionan la comparación.

## Fuentes de referencia

- Clementi, G. y Salias, L. G. *Minería de datos y técnicas de clustering para predecir deserción universitaria*. Informe de Trabajo Final de Investigación Operativa, UNICEN, 2025. En particular, secciones 3.2 y 5.
- Reunión con el profesor Gustavo Illescas del 17 de septiembre de 2026. Transcripción utilizada para precisar el origen, el foco comparativo y el criterio de ajuste del alcance.

## Primera comparación: K-Means con siete grupos

Para ejecutar preparación, referencia jerárquica y comparación K-Means, sin ejecutar el análisis extra:

```bash
ANALYSIS_DATE=2026-10-01 uv run python main.py --analisis kmeans
```

La fecha corresponde a la verificación de la migración y debe conservarse para comparar la misma entrada. Sin `ANALYSIS_DATE`, se utiliza el día de ejecución. El comando original sin argumentos sigue ejecutando el análisis extra heredado.

`src/clustering/kmeans.py` recibe el diccionario del análisis preliminar. Utiliza exactamente `alumnos_s_avanzados_sc`, sin etiquetas como predictores, y verifica el orden de filas contra la tabla original. Conserva `id_alumno` por separado para exportar las asignaciones. La entrada incluye `deserto`, como en el jerárquico: sus diferencias entre perfiles son descriptivas y no constituyen una validación independiente de la deserción.

El protocolo fija `k=7`, `init="k-means++"`, `n_init=25`, `algorithm="lloyd"`, `max_iter=300` y `tol=1e-4`. La ejecución presentada utiliza la semilla 123, seleccionando la menor inercia entre sus 25 inicializaciones. La estabilidad se evalúa también con semillas 0 a 8, conservando todos los demás parámetros. No se elige la semilla por su Silhouette ni por su coincidencia con el jerárquico.

Las tablas se guardan en `output/kmeans/`:

| Archivo | Contenido |
|---|---|
| `asignaciones.csv` | Fila de entrada, identificador, grupos de ambos métodos y Silhouette individual. |
| `perfiles.csv` | Cantidad, proporción, media, mediana y desvío muestral de cada variable en unidades originales. |
| `tamanos.csv` | Tamaños y proporciones de ambos métodos. |
| `correspondencia.csv` | Cantidades: filas jerárquicas, columnas K-Means. |
| `correspondencia_proporciones.csv` | Correspondencia normalizada por cada grupo jerárquico. |
| `metricas.csv` | Silhouette de ambos métodos sobre todos los estudiantes, inercia K-Means y ARI contra la referencia. |
| `estabilidad.csv` | Inercia, iteraciones, Silhouette y ARI por semilla. |
| `asignaciones_estabilidad.csv` | Asignaciones de cada semilla por estudiante. |
| `ari_entre_semillas.csv` | ARI para todos los pares de ejecuciones. |
| `centros_estandarizados.csv` | Centros de la ejecución principal. |
| `configuracion.json` | Fecha, variables, dimensiones, parámetros, semillas, versiones y huellas de entrada y referencia. |

En `output/graficos/kmeans/` se generan seis PNG: correspondencia, correspondencia en proporciones, tamaños, Silhouette, perfiles estandarizados y estabilidad. Los números de los grupos no indican correspondencia entre métodos ni entre semillas; la tabla de correspondencia y ARI permiten compararlos sin esa suposición. ARI mide concordancia entre particiones, no calidad del agrupamiento.

La primera ejecución y sus límites se registran en [docs/resultados-kmeans.md](docs/resultados-kmeans.md). Los archivos de salida con información estudiantil permanecen excluidos de Git.

Para verificar el contrato de entrada y las exportaciones:

```bash
uv run pytest -q
```
