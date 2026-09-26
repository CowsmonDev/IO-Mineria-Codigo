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
