# Criterios del trabajo comparativo

Fecha de registro: 3 de octubre de 2026.

Esta nota registra las decisiones de alcance acordadas para el trabajo final. El documento destinado al profesor se desarrolla en [informe.md](informe.md).

## Objetivo acordado

Comparar la segmentación obtenida mediante clustering jerárquico en el estudio de Clementi y Salias con las segmentaciones obtenidas mediante K-Means y DBSCAN, utilizando exactamente los mismos datos preparados como entrada.

La comparación estudia cómo cambia la formación de los grupos y en qué medida se conservan, dividen o fusionan los perfiles estudiantiles originales. El resultado jerárquico funciona como referencia, sin considerarse una clasificación verdadera que los demás algoritmos deban reproducir.

## Elementos que se conservan

- La fuente de datos y la población de estudiantes del análisis original.
- Los criterios de inclusión y exclusión, los filtros y el tratamiento de los datos.
- Las variables utilizadas para el clustering en el estudio original.
- Las transformaciones y la estandarización aplicadas antes del agrupamiento.
- El código original y sus resultados de clustering jerárquico como referencia fija de la comparación.

La entrada común es la matriz de estudiantes y variables preparada y estandarizada antes del clustering. Las etiquetas de los grupos originales no se incorporan como variables de entrada a K-Means ni a DBSCAN.

El clustering jerárquico conserva la segmentación del trabajo original: los mismos siete grupos y la misma composición de estudiantes en cada grupo. Esa referencia está verificada y permanece fija durante la comparación.

K-Means y DBSCAN se aplicarán sobre la misma entrada y podrán producir asignaciones diferentes. Esas diferencias respecto de la segmentación jerárquica original son el objeto de la comparación. La cantidad de grupos de K-Means se definirá en el protocolo; la de DBSCAN surgirá de sus parámetros de densidad.

## Papel de LASSO

El estudio original incluye regresión logística con penalización LASSO y clustering jerárquico como análisis separados.

En el código original, los coeficientes de LASSO se calculan y se muestran, pero no se utilizan para seleccionar ni ponderar las variables del clustering. El agrupamiento utiliza la tabla preparada, estandarizada posteriormente.

Por lo tanto, este trabajo conserva el análisis LASSO como antecedente. No modifica sus parámetros, no reinterpreta sus resultados ni desarrolla una comparación de modelos de regresión. Su mención en el informe sirve para contextualizar el estudio previo y delimitar la extensión realizada.

## Cercanía y agrupamiento

La referencia jerárquica utiliza distancia euclídea y enlace Ward (`ward.D2` en R). La distancia describe la cercanía entre estudiantes; el enlace establece cómo se fusionan los grupos.

K-Means y DBSCAN recibirán la misma matriz estandarizada. K-Means agrupa alrededor de centros minimizando distancias euclídeas cuadradas; DBSCAN identifica agrupamientos por densidad mediante vecindades euclídeas. Sus parámetros propios deben documentarse y justificarse.

## Resultados que se compararán

- Cantidad de grupos, tamaños y proporciones de estudiantes asignados.
- Cohesión y separación mediante Silhouette, cuando corresponda calcularlo.
- Correspondencia de integrantes entre los grupos de cada método.
- Características académicas de los perfiles, descritas en las unidades originales.
- Perfiles que se conservan, se dividen o se fusionan.
- Estudiantes considerados ruido por DBSCAN y su procedencia en los grupos originales.
- Sensibilidad de los resultados a las inicializaciones de K-Means y a los parámetros de DBSCAN.

Si Silhouette de DBSCAN se calcula excluyendo el ruido, se informarán la cantidad y proporción de estudiantes incluidos. No se presentará ese valor como si tuviera la misma cobertura que una evaluación sobre toda la población.

## Estado del protocolo y decisiones pendientes

- La entrada común quedó registrada para la fecha 2026-10-01: 2.587 estudiantes y diez variables; ver [resultados-kmeans.md](resultados-kmeans.md).
- K-Means se ejecuta con siete grupos, k-means++, 25 inicializaciones y semilla 123. La primera implementación examinó semillas adicionales, pero la ejecución actual se limita al agrupamiento y sus gráficos. El protocolo de estabilidad se retomará al abordar la comparación; ver [resultados-kmeans.md](resultados-kmeans.md).
- DBSCAN ejecuta una configuración explícita, inicialmente eps=1.5 y min_samples=5. Primero se inspeccionan los grupos y gráficos; la exploración comparativa y la justificación final de parámetros quedan pendientes. Ver [resultados-dbscan.md](resultados-dbscan.md).
- Acordar si se explorarán otras cantidades de grupos para K-Means como análisis complementario.

## Etapa actual

La implementación actual prepara una entrada común, ejecuta los tres métodos y muestra resultados básicos y gráficos. La comparación sistemática prevista en esta nota se realizará posteriormente. Se retiraron los módulos de evaluación comparativa y exportación para mantener el código centrado en esta etapa.

## Documentación

`docs/` se utilizará como carpeta de trabajo en Obsidian. Se mantendrán las notas y el informe en Markdown. El PDF se generará cuando sea necesario compartir una versión con el profesor.

El informe distinguirá entre los resultados jerárquicos del estudio original y los nuevos resultados de K-Means y DBSCAN.

## Referencias de esta nota

- [Informe de Clementi y Salias](referencias/IO-Mineria-Informe-Clementi-Salias.pdf), secciones 3.1, 3.2, 3.2.1 y 5.
- [Código original del análisis preliminar](../Legacy/scripts/script_analisis_preliminar_2025.R), selección de variables, LASSO, estandarización y clustering jerárquico.
- [Preparación común](../src/data/preparacion.py) y [ejecución unificada](../main.py).
- [Referencia jerárquica](../src/clustering/jerarquico.py), [K-Means](../src/clustering/kmeans.py) y [DBSCAN](../src/clustering/dbscan.py).
- [Documentación de clustering de scikit-learn](https://scikit-learn.org/stable/modules/clustering.html).
