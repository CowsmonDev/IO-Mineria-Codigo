# Comparación de clustering jerárquico, K-Means y DBSCAN para la segmentación de estudiantes de Ingeniería de Sistemas

**Trabajo final de Investigación Operativa**

Facultad de Ciencias Exactas — Universidad Nacional del Centro de la Provincia de Buenos Aires

**Autor:** [Completar]

**Profesor:** [Completar]

**Fecha de presentación:** [Completar]

> Estado: borrador inicial. Los textos entre corchetes indican información pendiente. Las tablas de resultados se completarán con los experimentos; no contienen resultados nuevos confirmados.

## Resumen

[Redactar al finalizar el análisis: problema, objetivo, datos utilizados, métodos comparados, principales resultados y conclusión.]

**Palabras clave:** clustering; segmentación estudiantil; clustering jerárquico; K-Means; DBSCAN; deserción universitaria.

## 1. Introducción y antecedentes

El estudio de Clementi y Salias analizó la deserción en la carrera de Ingeniería de Sistemas de la Facultad de Ciencias Exactas de la UNICEN a partir de datos académicos del sistema SIU Guaraní. Entre las técnicas empleadas se encuentran la regresión logística con penalización LASSO y el clustering jerárquico aglomerativo. Este último permitió describir perfiles estudiantiles a partir de una segmentación en siete grupos.

En la sección de trabajos futuros, los autores propusieron incorporar información socioeconómica y contextual y aplicar K-Means y DBSCAN para contrastar la estabilidad de los perfiles hallados. El presente trabajo retoma la comparación de algoritmos sobre la base existente, conservando la población, las variables y la preparación utilizadas en el agrupamiento original.

Esta extensión compara los perfiles jerárquicos del estudio original con los obtenidos mediante K-Means y DBSCAN.

## 2. Objetivos y alcance

### 2.1. Objetivo general

Comparar la segmentación obtenida mediante clustering jerárquico con las obtenidas mediante K-Means y DBSCAN, utilizando exactamente la misma entrada de datos, para determinar en qué medida se conservan o cambian los perfiles estudiantiles del estudio original.

### 2.2. Objetivos específicos

1. Documentar la entrada de datos y la configuración del agrupamiento jerárquico original, cuyos siete grupos y sus integrantes se conservan como referencia fija.
2. Aplicar K-Means y DBSCAN sobre la misma matriz preparada y estandarizada.
3. Comparar la cantidad, los tamaños, la cohesión y la separación de los grupos obtenidos.
4. Analizar la correspondencia entre las asignaciones y caracterizar los perfiles que se conservan, se dividen o se fusionan.
5. Describir el ruido identificado por DBSCAN y la sensibilidad de las segmentaciones a los parámetros evaluados.

### 2.3. Alcance

El trabajo conserva la fuente de datos, los criterios de selección de estudiantes, las variables, las transformaciones y la estandarización del análisis de referencia.

La regresión logística con LASSO se mantiene como antecedente del estudio. En el código original, sus coeficientes no determinan la selección ni la ponderación de las variables utilizadas por el clustering. La extensión se concentra en los agrupamientos y no modifica ni evalúa nuevamente el modelo LASSO.

La segmentación jerárquica original se preserva como referencia fija, con sus siete grupos y la composición de estudiantes de cada uno. Las nuevas segmentaciones que se comparan con ella son las obtenidas mediante K-Means y DBSCAN.

## 3. Datos y preparación común

### 3.1. Población y fuente de datos

[Describir la procedencia de los datos, el período considerado, los criterios de inclusión y exclusión y la cantidad final de estudiantes. Verificar estos detalles contra el código y los datos utilizados.]

### 3.2. Variables utilizadas

[Completar con todas las variables que efectivamente integran la matriz de clustering. No deducir la lista a partir de los coeficientes LASSO.]

| Variable | Descripción | Unidad o codificación | Transformación previa |
|---|---|---|---|
| [Completar] | [Completar] | [Completar] | [Completar] |

### 3.3. Transformaciones y estandarización

El código de referencia transforma las variables temporales a días y estandariza las columnas numéricas restando su media y dividiendo por su desvío estándar muestral. La misma matriz resultante se utilizará como entrada para los tres métodos.

[Documentar el tratamiento de valores faltantes y cualquier otra operación efectivamente aplicada. Registrar la dimensión final de la matriz y la correspondencia entre sus filas y los estudiantes.]

Las etiquetas del clustering jerárquico se conservarán para comparar las asignaciones, sin incorporarlas como variables de entrada a los métodos alternativos. Los perfiles se describirán en las unidades originales para facilitar su interpretación.

## 4. Metodología comparativa

### 4.1. Clustering jerárquico de referencia

El informe original utiliza distancia euclídea y enlace Ward (`ward.D2` en R). Este enlace fusiona grupos procurando minimizar el incremento de la variación interna. Según el informe, el análisis de Silhouette fundamentó la elección de siete grupos, obtenidos mediante un corte del dendrograma a altura 35.

[Detallar los parámetros del agrupamiento jerárquico original que se conserva como referencia de la comparación.]

### 4.2. K-Means

K-Means forma una cantidad prefijada de grupos alrededor de centros, minimizando la suma de distancias euclídeas cuadradas entre las observaciones y el centro de su grupo.

La primera comparación utiliza siete grupos, manteniendo la cantidad de la referencia jerárquica. Se conserva una ejecución principal prefijada y se evalúa la sensibilidad a la inicialización. La ejecución inicial y sus resultados se registran en [resultados-kmeans.md](resultados-kmeans.md).

| Decisión | Configuración |
|---|---|
| Cantidad de grupos | 7 |
| Inicialización | k-means++; algoritmo Lloyd, máximo 300 iteraciones y tolerancia 0,0001 |
| Cantidad de inicializaciones por ejecución | 25 |
| Semillas y repeticiones | Principal: 123; adicionales: 0 a 8 |
| Criterio de selección de la ejecución presentada | Semilla 123 prefijada; menor inercia entre sus 25 inicializaciones |

### 4.3. DBSCAN

DBSCAN forma grupos a partir de regiones densas, utilizando un radio de vecindad (`eps`) y un mínimo de observaciones (`min_samples`). Se utilizarán vecindades euclídeas sobre la misma matriz estandarizada. La cantidad de grupos surge del análisis y algunas observaciones pueden quedar clasificadas como ruido.

No se exigirá que DBSCAN produzca siete grupos. Se documentará cómo se seleccionan sus parámetros y cómo cambian los resultados entre las configuraciones examinadas.

| Decisión | Configuración |
|---|---|
| Valores de `eps` evaluados | [Definir y justificar] |
| Valores de `min_samples` evaluados | [Definir y justificar] |
| Criterio de elección de la configuración presentada | [Definir] |
| Tratamiento del ruido en las métricas | Informar explícitamente las observaciones incluidas y excluidas |

### 4.4. Criterios de comparación

La comparación considerará la cantidad y el tamaño de los grupos, Silhouette, la correspondencia de sus integrantes y las características académicas de los perfiles. No se compararán las etiquetas por su número: el grupo 1 de un método no necesariamente corresponde al grupo 1 de otro.

Se construirán tablas de correspondencia entre cada método alternativo y la referencia jerárquica. Para DBSCAN se incluirá una categoría de ruido en esas tablas. La estabilidad se examinará mediante distintas inicializaciones de K-Means y la sensibilidad a los parámetros de DBSCAN, diferenciando estas pruebas de la coincidencia entre métodos.

Silhouette se informará cuando la partición permita calcularlo. Si se excluye el ruido de DBSCAN, se indicarán la cantidad y la proporción de estudiantes evaluados. Su valor no se interpretará como una comparación sobre toda la población sin considerar esa diferencia de cobertura.

### 4.5. Registro de los experimentos

Cada experimento conservará su configuración, las versiones de las herramientas utilizadas, las asignaciones obtenidas, las métricas y las tablas o gráficos necesarios para reproducir e interpretar el resultado.

Para K-Means se ejecuta `ANALYSIS_DATE=2026-10-01 uv run python main.py --analisis kmeans`. Las tablas y la configuración se exportan en `output/kmeans/`, y los gráficos en `output/graficos/kmeans/`. El [README](../README.md#primera-comparación-k-means-con-siete-grupos) describe las salidas y el protocolo.

[Completar el registro de DBSCAN cuando se implemente.]

## 5. Resultados

### 5.1. Resultados del clustering jerárquico original

[Resumir los siete perfiles del estudio original, sus integrantes, tamaños y métricas. Estos resultados constituyen la referencia fija para las comparaciones siguientes.]

### 5.2. Resultados de K-Means

La ejecución principal sobre 2.587 estudiantes obtuvo Silhouette de 0,365474, frente a 0,295444 del jerárquico, y ARI contra la referencia de 0,670893. El mínimo ARI entre semillas fue 0,666514, por lo que existe sensibilidad a la inicialización que debe considerarse al interpretar los perfiles. El detalle reproducible está en [resultados-kmeans.md](resultados-kmeans.md).

[Completar la interpretación de los perfiles a partir de las tablas exportadas.]

### 5.3. Resultados de DBSCAN

[Presentar las configuraciones evaluadas, la elegida, la cantidad y los tamaños de los grupos, el ruido, las métricas calculables y los perfiles.]

### 5.4. Comparación general

| Método | Configuración | Cantidad de grupos | Estudiantes agrupados | Ruido | Silhouette | Población evaluada para Silhouette |
|---|---|---|---|---|---|---|
| Jerárquico | [Configuración original] | 7 | [Completar] | No aplica | [Completar] | [Completar] |
| K-Means | [Completar] | [Completar] | [Completar] | No aplica | [Completar] | [Completar] |
| DBSCAN | [Completar] | [Completar] | [Completar] | [Completar] | [Valor o motivo por el que no aplica] | [Completar] |

### 5.5. Correspondencia de grupos y perfiles

[Incorporar las tablas de correspondencia y describir qué perfiles se conservan, se dividen o se fusionan. Fundamentar las interpretaciones con la composición de los grupos y los resúmenes de variables.]

## 6. Discusión y limitaciones

[Analizar qué diferencias se relacionan con el criterio de agrupamiento de cada método. Considerar conjuntamente las métricas, la cobertura y la interpretación de los perfiles.]

[Discutir la sensibilidad de los métodos alternativos a sus parámetros y las limitaciones de los datos. Para K-Means y DBSCAN, la coincidencia con la referencia no equivale por sí sola a una mejor segmentación.]

## 7. Conclusiones

[Responder al objetivo general: qué perfiles se conservaron, cuáles cambiaron, qué diferencias aportó cada método y qué evidencia sostiene esas conclusiones. No redactar conclusiones antes de obtener los resultados.]

## 8. Referencias

- Clementi, G. y Salias, L. G. (2025). *Minería de datos y técnicas de clustering para predecir deserción universitaria*. Informe de Trabajo Final de Investigación Operativa, UNICEN. [PDF original](referencias/IO-Mineria-Informe-Clementi-Salias.pdf).
- [Documentación de clustering de scikit-learn](https://scikit-learn.org/stable/modules/clustering.html).
- [Incorporar las referencias metodológicas utilizadas y unificar el formato bibliográfico.]

## Anexo A. Configuraciones y resultados complementarios

[Incluir el detalle de las ejecuciones, las configuraciones adicionales y las tablas extensas que respaldan el análisis.]
