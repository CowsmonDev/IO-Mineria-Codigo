# Anexo técnico de la experiencia con DBSCAN

El [informe final](experiencia-dbscan.pdf) presenta los cinco casos representativos y la decisión de no adoptar DBSCAN como segmentación seleccionada bajo el protocolo estudiado. Se conserva su [fuente editable](experiencia-dbscan.docx). Este anexo reúne la evidencia técnica de las exploraciones del 5 de octubre de 2026, con fecha de análisis `2026-10-01`; no abre una nueva búsqueda ni selecciona otros parámetros.

Las cifras se trasladaron de los registros de las exploraciones, sin volver a ejecutar sus búsquedas al consolidar la documentación. Los cinco casos del informe fueron recalculados para su verificación el 10 de octubre de 2026. La implementación, los casos fijos y sus gráficos permanecen disponibles como evidencia experimental.

## Entrada y criterios comunes

Se utilizaron 2.587 alumnos y diez atributos académicos, incluido `deserto`, estandarizados con desvío muestral (`ddof=1`) y distancia euclídea. DBSCAN y el jerárquico recibieron la misma matriz; las etiquetas y los IDs no se usaron como atributos. La referencia jerárquica utiliza Ward y corte a altura 35. Su [equivalencia con R](verificacion-fechas-r-python.md) está verificada para las entradas ensayadas.

La huella SHA-256 registrada para los bytes de la matriz NumPy estandarizada es `39ba3042df7aba74b04409a693c56f36f05f7008c18efc45ffd92c2651dd48c7`.

Silhouette excluye ruido y se informa junto con su población evaluada; con un solo grupo no es calculable. La concentración del grupo mayor usa sólo alumnos agrupados. ARI mide concordancia entre particiones, no aciertos; frente al jerárquico se calcula sobre alumnos agrupados por DBSCAN, conservando las etiquetas de referencia. Para sensibilidad entre configuraciones se restringe a alumnos agrupados en ambas y se acompaña de cambios ruido/grupo y cobertura. La proporción de deserción es descriptiva porque `deserto` participa en la entrada.

## Cercanía y formación de grupos en diez dimensiones

Cada alumno es un punto con diez coordenadas, una por atributo estandarizado. La distancia euclídea entre dos alumnos se calcula tomando la raíz cuadrada de la suma de las diferencias al cuadrado en las diez coordenadas. Dos puntos son vecinos si su distancia es menor o igual que `eps`. Un núcleo tiene al menos `min_samples` puntos en su vecindad, incluido él mismo; los grupos conectan núcleos vecinos y añaden puntos de borde. Una cadena de núcleos puede reunir alumnos que no sean vecinos directos.

DBSCAN se ejecuta sobre esas diez dimensiones. PCA produce una proyección en dos ejes para visualizar los resultados; las distancias y vecindades del algoritmo no se calculan sobre esa proyección. El informe final explica este procedimiento antes de interpretar los resultados.

## Primera exploración de dieciséis configuraciones

Se inspeccionó la curva de vecinos. Para min_samples 5, 10 y 20, las medianas de distancia al vecino que completa el mínimo son 0,162, 0,281 y 0,386; los percentiles 90 son 1,301, 1,520 y 1,774. Hay una zona densa de distancias pequeñas y una cola de alumnos más aislados; no se asumió un codo único como selección automática.

La primera tanda fue eps={0,6; 0,8; 1,0; 1,5} con min_samples={5; 10; 20}. Como persistía un grupo dominante, se añadieron cuatro radios con min_samples=10: 0,3 y 0,4 para examinar fragmentación, y 0,9 y 1,1 para sensibilidad local. Total: dieciséis configuraciones explícitas.

Silhouette excluye ruido. «Evaluados» es la población usada para ese cálculo, no la población total. Cuando queda un solo grupo se registra como no calculable, no como cero.

| eps | min_samples | Grupos | Ruido | Ruido % | Silhouette | Evaluados | Grupo mayor |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.6 | 5 | 9 | 469 | 18.13 % | -0,1280 | 2118 | 2036 |
| 0.8 | 5 | 6 | 342 | 13.22 % | -0,0179 | 2245 | 2144 |
| 1 | 5 | 4 | 292 | 11.29 % | 0,0197 | 2295 | 2195 |
| 1.5 | 5 | 1 | 194 | 7.50 % | No calculable | 0 | 2393 |
| 0.3 | 10 | 18 | 1146 | 44.30 % | 0,0961 | 1441 | 886 |
| 0.4 | 10 | 10 | 895 | 34.60 % | -0,1069 | 1692 | 1432 |
| 0.6 | 10 | 5 | 560 | 21.65 % | -0,0148 | 2027 | 1942 |
| 0.8 | 10 | 3 | 409 | 15.81 % | 0,0444 | 2178 | 2109 |
| 0.9 | 10 | 3 | 358 | 13.84 % | 0,0621 | 2229 | 2147 |
| 1 | 10 | 3 | 339 | 13.10 % | 0,0669 | 2248 | 2162 |
| 1.1 | 10 | 3 | 313 | 12.10 % | 0,0778 | 2274 | 2183 |
| 1.5 | 10 | 1 | 208 | 8.04 % | No calculable | 0 | 2379 |
| 0.6 | 20 | 1 | 728 | 28.14 % | No calculable | 0 | 1859 |
| 0.8 | 20 | 2 | 494 | 19.10 % | 0,0096 | 2093 | 2061 |
| 1 | 20 | 2 | 401 | 15.50 % | 0,0364 | 2186 | 2137 |
| 1.5 | 20 | 1 | 236 | 9.12 % | No calculable | 0 | 2351 |

- Con eps=1,5 queda un único grupo para los tres mínimos probados.
- Con min_samples=5, radios menores forman grupos pequeños y uno muy grande. Silhouette es negativo con eps=0,6 y 0,8 y apenas positivo con eps=1,0.
- Con min_samples=10 y eps entre 0,8 y 1,1 aparecen tres grupos. El mayor concentra entre 2.109 y 2.183 alumnos; los otros son pequeños. El ruido baja de 409 a 313 alumnos y Silhouette sube de 0,0444 a 0,0778.
- El mayor Silhouette de la exploración es 0,0961 con eps=0,3 y mínimo 10, pero deja 44,3 % de alumnos como ruido y forma 18 grupos. Ese valor corresponde a una cobertura distinta y no justifica elegir la configuración.
- Con mínimo 20 predominan uno o dos grupos y crece el ruido.

Estas pruebas permiten calcular Silhouette para varias configuraciones, pero no muestran una segmentación claramente separada y distribuida entre varios perfiles de tamaño relevante.

## Perfiles y sensibilidad de la primera exploración

Para eps=1,1 y min_samples=10:

| Categoría | Alumnos | Finales aprobados, media | Promocionadas, media | Deserción |
|---|---:|---:|---:|---:|
| Grupo 1 | 2.183 | 1,887 | 0 | 100 % |
| Grupo 2 | 70 | 1,643 | 1 | 100 % |
| Grupo 3 | 21 | 2,333 | 2 | 100 % |
| Ruido | 313 | 9,249 | 1,431 | 76,36 % |

En esta configuración, los grupos pequeños se distinguen especialmente por la cantidad de promociones, mientras el grupo principal incluye alumnos de bajo avance y sin promociones. El ruido contiene trayectorias de mayor avance medio y todos los 74 alumnos marcados como no desertores.

Los 74 no desertores quedaron como ruido en las dieciséis configuraciones, no solo en la representativa. Ruido no significa deserción ni error: refleja que no quedaron integrados en regiones suficientemente densas bajo esos parámetros. Como deserto participa en la matriz, estas proporciones son descriptivas y no validan una predicción.

Con mínimo 10, se compararon radios vecinos 0,8–0,9, 0,9–1,0 y 1,0–1,1. Entre los alumnos agrupados en ambas configuraciones, ARI=1 en los tres pares (2.178, 2.229 y 2.248 alumnos respectivamente).

Esto indica que sus agrupamientos se conservan en el subconjunto común; cambia qué alumnos pasan del ruido a un grupo. No demuestra estabilidad de toda la población ni frente a otras muestras o parámetros fuera del intervalo probado.

## Ampliación de radios y densidades

La ampliación inicial examinó eps={0,2; 0,3; 0,4; 0,5; 0,6; 0,7} con mínimos {3; 5; 8; 15}, más eps={0,5; 0,7} con mínimo 10. Después se revisó el entorno de eps=0,5 con radios 0,45 y 0,55 y mínimos 8, 10 y 12, además de 0,5/12. Para una solución fragmentada se probaron radios 0,18 y 0,22 con mínimo 5. Total: 35 configuraciones en esta tanda, una de ellas repetida de la exploración anterior.

Silhouette se calcula sin ruido; sus valores no tienen necesariamente la misma cobertura. El porcentaje del grupo mayor usa solo los alumnos agrupados.

| eps | min_samples | Grupos | Ruido | Silhouette | Grupo mayor / agrupados |
|---|---:|---:|---:|---:|---:|
| 0,2 | 3 | 99 | 38,3 % | 0,3170 | 46,1 % |
| 0,3 | 3 | 79 | 30,0 % | 0,0937 | 49,6 % |
| 0,4 | 3 | 35 | 23,8 % | -0,2862 | 75,1 % |
| 0,5 | 3 | 32 | 19,5 % | -0,2755 | 73,5 % |
| 0,6 | 3 | 18 | 15,3 % | -0,1560 | 94,4 % |
| 0,7 | 3 | 15 | 12,9 % | -0,0714 | 94,7 % |
| 0,18 | 5 | 59 | 45,8 % | 0,4823 | 38,8 % |
| 0,2 | 5 | 53 | 45,1 % | 0,3516 | 48,3 % |
| 0,22 | 5 | 46 | 42,1 % | 0,2581 | 49,8 % |
| 0,3 | 5 | 44 | 36,0 % | 0,0877 | 54,2 % |
| 0,4 | 5 | 14 | 27,8 % | -0,1721 | 78,7 % |
| 0,5 | 5 | 18 | 23,4 % | -0,1825 | 76,4 % |
| 0,6 | 5 | 9 | 18,1 % | -0,1280 | 96,1 % |
| 0,7 | 5 | 4 | 15,2 % | -0,0198 | 96,6 % |
| 0,2 | 8 | 34 | 51,1 % | 0,3267 | 52,9 % |
| 0,3 | 8 | 23 | 42,4 % | 0,1116 | 59,5 % |
| 0,4 | 8 | 10 | 31,9 % | -0,0996 | 81,9 % |
| 0,45 | 8 | 9 | 28,5 % | -0,0443 | 80,2 % |
| 0,5 | 8 | 9 | 26,7 % | -0,0445 | 79,3 % |
| 0,55 | 8 | 6 | 22,7 % | -0,0465 | 96,6 % |
| 0,6 | 8 | 4 | 21,2 % | -0,0221 | 97,2 % |
| 0,7 | 8 | 4 | 16,7 % | -0,0415 | 97,0 % |
| 0,45 | 10 | 7 | 30,6 % | -0,0332 | 81,8 % |
| 0,5 | 10 | 7 | 29,0 % | -0,0419 | 81,5 % |
| 0,55 | 10 | 6 | 23,8 % | -0,0066 | 96,0 % |
| 0,7 | 10 | 4 | 18,0 % | -0,0377 | 97,7 % |
| 0,45 | 12 | 8 | 31,9 % | -0,0339 | 83,0 % |
| 0,5 | 12 | 6 | 30,2 % | -0,0284 | 82,1 % |
| 0,55 | 12 | 5 | 25,5 % | -0,0027 | 97,4 % |
| 0,2 | 15 | 16 | 60,8 % | 0,3109 | 64,4 % |
| 0,3 | 15 | 12 | 49,2 % | 0,0986 | 66,5 % |
| 0,4 | 15 | 5 | 39,3 % | -0,0124 | 86,9 % |
| 0,5 | 15 | 8 | 32,4 % | -0,0675 | 84,4 % |
| 0,6 | 15 | 3 | 25,2 % | -0,0140 | 98,4 % |
| 0,7 | 15 | 2 | 20,4 % | -0,0248 | 98,9 % |

Con eps=0,5 y mínimo 10 se obtienen siete grupos, de tamaños 1.498, 152, 15, 82, 61, 19 y 11, más 749 alumnos como ruido (28,95 %). Silhouette es −0,0419 y el mayor grupo concentra 81,5 % de los agrupados.

Los grupos pequeños se distinguen fuertemente por valores discretos de los atributos: por ejemplo, los grupos 2, 4, 5 y 6 tienen exactamente 1, 2, 3 y 4 finales desaprobados respectivamente; el grupo 3 tiene una promoción. Esto describe una separación asociada a esos atributos, no demuestra por sí solo perfiles académicos amplios e independientes.

Con eps=0,2 y mínimo 5 se obtienen 53 grupos y Silhouette de 0,3516, pero queda 45,15 % como ruido. Al reducir eps a 0,18 aparecen 59 grupos y Silhouette de 0,4823, con 45,84 % de ruido. Son soluciones mucho más fragmentadas y muchas agrupaciones tienen pocos alumnos; su mayor Silhouette no justifica automáticamente elegirlas.

## Sensibilidad a parámetros y orden de filas

Se compararon asignaciones alineadas por ID, considerando ARI únicamente entre alumnos agrupados en ambas configuraciones. También se registraron cambios de condición de ruido y Jaccard de las poblaciones agrupadas. No se trató el ruido como un cluster homogéneo para calcular ARI.

| Configuraciones | Alumnos agrupados en ambas | ARI en comunes | Cambios ruido/grupo |
|---|---:|---:|---:|
| 0,45/10 → 0,5/10 | 1.795 | 1 | 43 |
| 0,5/10 → 0,55/10 | 1.838 | 0,0957 | 134 |
| 0,5/8 → 0,5/10 | 1.838 | 0,9988 | 58 |
| 0,5/10 → 0,5/12 | 1.805 | 1 | 33 |
| 0,18/5 → 0,2/5 | 1.401 | 0,7441 | 18 |
| 0,2/5 → 0,22/5 | 1.419 | 0,9024 | 79 |

La solución de siete grupos se conserva en el subconjunto común entre 0,45 y 0,5, y es poco sensible al mínimo en el entorno probado. Sin embargo, al subir eps de 0,5 a 0,55 varios grupos se fusionan: aparecen seis grupos y el mayor reúne 1.893 alumnos, 96 % de los agrupados. No se puede describir esa solución como estable en todo el intervalo.

Se probaron cinco permutaciones de la entrada para 0,5/10 y 0,2/5, manteniendo los datos y parámetros. En 0,5/10 las particiones coincidieron completamente y ningún alumno cambió su condición de ruido. En 0,2/5 ARI en comunes fue 0,9981, sin cambios ruido/grupo; se observan pequeñas diferencias de asignación compatibles con puntos de borde.

Reproducibilidad al cambiar el orden no equivale a estabilidad frente a los parámetros o cambios en la muestra. No se realizaron pruebas de remuestreo.

## Proyección de los experimentos con PCA

Cada alumno ocupa un punto en el espacio original de diez atributos estandarizados. Se ajustó una única PCA de dos componentes sobre toda la matriz para visualizar las soluciones 0,5/10 (siete grupos) y 1,1/10 (tres grupos) con la misma proyección y escalas.

- Componente 1: 45,7919 % de la varianza.
- Componente 2: 22,7740 %.
- Total representado: 68,5660 %.

Los ejes son combinaciones lineales de los atributos, no atributos individuales. Cada punto corresponde a un alumno; color indica el grupo y gris indica ruido. Los puntos coincidentes pueden superponerse. Las etiquetas se calcularon en diez dimensiones, no sobre la proyección. PCA se usa solo para visualizar y no modifica la entrada de DBSCAN.

La proyección pierde aproximadamente 31,4 % de la varianza: grupos distintos pueden verse superpuestos y la distancia dibujada no equivale a la distancia completa usada por DBSCAN. La nube ilustra cambios de asignación y ruido, no reemplaza el análisis de perfiles o sensibilidad.

El informe final también muestra los casos `1,175/4` y `0,18/5` con una proyección común. Las proyecciones de cada figura se usan para visualizar; los agrupamientos se calculan siempre sobre los diez atributos.

## Grilla de 470 configuraciones y concordancia

Se exploró si DBSCAN podía producir **siete grupos con hasta 15 % de ruido y una estructura cercana al jerárquico**, sin cambiar los alumnos, atributos ni estandarización. Es una búsqueda de concordancia orientada por la referencia; no es una validación independiente de los siete perfiles ni demuestra que el jerárquico sea una clasificación verdadera.

La entrada contiene 2.587 alumnos y diez atributos. Su SHA-256, sobre los bytes de la matriz NumPy de valores estandarizados, es `39ba3042df7aba74b04409a693c56f36f05f7008c18efc45ffd92c2651dd48c7`.

La búsqueda principal fue una grilla fija de **470 configuraciones**:

- `eps`: de 0,350 a 1,500 inclusive, con paso 0,025 (47 valores).
- `min_samples`: 2, 3, 4, 5, 6, 8, 10, 12, 15 y 20.
- Distancia euclídea sobre la misma matriz estandarizada en diez dimensiones.
- Referencia jerárquica: Ward y corte a altura 35, siete grupos.

Para cada configuración se registraron grupos, ruido, cobertura, tamaños y ARI frente al jerárquico **solo sobre alumnos no marcados como ruido por DBSCAN**. Las etiquetas jerárquicas se conservaron en ese subconjunto; no se volvió a ajustar el árbol. ARI expresa concordancia entre particiones, no porcentaje de aciertos. Valores próximos a cero indican poca concordancia ajustada por azar.

Se encontraron 17 configuraciones con siete grupos; ocho cumplen el límite de ruido. Entre estas ocho se ordenaron los candidatos por ARI descendente. También se inspeccionaron la configuración con menor ruido, la de mayor ARI con siete grupos y la alternativa anterior `0,5/10`. Silhouette se calculó únicamente para esas cinco configuraciones, excluyendo ruido.

Tamaños ordenados de mayor a menor; la proporción del grupo mayor se calcula entre alumnos agrupados, excluyendo ruido.

| eps / min_samples | Grupos | Ruido | Tamaños de los grupos | Grupo mayor | ARI frente al jerárquico | Silhouette sin ruido |
|---|---:|---:|---|---:|---:|---:|
| 1,175 / 4 | 7 | 244 (9,43 %) | 2215, 85, 28, 5, 4, 4, 2 | 94,54 % | 0,040746 | 0,108837 |
| 1,150 / 4 | 7 | 250 (9,66 %) | 2211, 83, 28, 5, 4, 4, 2 | 94,61 % | 0,040398 | 0,103179 |
| 0,775 / 4 | 7 | 339 (13,10 %) | 2144, 64, 18, 8, 5, 5, 4 | 95,37 % | 0,037087 | −0,022203 |
| 1,500 / 3 | 7 | 152 (5,88 %) | 2407, 9, 6, 4, 3, 3, 3 | 98,85 % | 0,013643 | 0,439844 |
| 0,500 / 10 | 7 | 749 (28,95 %) | 1498, 152, 82, 61, 19, 15, 11 | 81,50 % | 0,048600 | −0,041918 |

**Obtener siete grupos con poco ruido es posible en esta grilla, pero no consigue la separación buscada.** En las ocho configuraciones que cumplen la meta, el grupo mayor concentra entre 94,54 % y 99,25 % de los alumnos agrupados. El mejor ARI dentro de ellas es apenas 0,040746. El máximo ARI entre todas las configuraciones de siete grupos es 0,048600, con casi 29 % de ruido.

El Silhouette de `1,5/3` es mayor, pero convive con un grupo de 2.407 alumnos y seis grupos de 3 a 9 alumnos. Esta combinación muestra por qué una puntuación aislada tampoco basta para escoger una segmentación.

## Composición del candidato con siete grupos y poco ruido

En `eps=1,175; min_samples=4`, el grupo DBSCAN de 2.215 alumnos mezcla:

- 331 de los 332 alumnos del grupo jerárquico 2.
- 340 de los 355 del grupo jerárquico 5.
- Los 903 del grupo jerárquico 6.
- 579 de los 636 del grupo jerárquico 7.
- 62 del grupo jerárquico 3.

Todos los alumnos del grupo jerárquico 1 (51) y del grupo 4 (74) quedan como ruido. Los 74 alumnos con `deserto=0` también quedan como ruido en este candidato. Esto limita qué perfiles se comparan mediante el ARI sin ruido. En `1,5/3`, tres de esos 74 alumnos sí quedan agrupados: el comportamiento no es idéntico para todas las configuraciones.

La tabla cruzada incluye ruido para hacer visibles esas exclusiones. Tener siete etiquetas no implica conservar siete perfiles semejantes a los jerárquicos.

## Sensibilidad de los candidatos de la grilla

Se evaluaron vecinos de cada una de las cinco configuraciones inspeccionadas: `eps ±0,025` con el mismo mínimo y `min_samples ±1` con el mismo radio, sin bajar de 2. Son pruebas adicionales a la grilla. Se registraron cantidad de grupos, cambios de condición ruido/agrupado, Jaccard de alumnos agrupados y ARI sobre alumnos agrupados en ambas ejecuciones.

Para el candidato `1,175/4`:

| Parámetros vecinos | Grupos | Ruido | Cambios ruido/agrupado | ARI entre alumnos agrupados en ambas |
|---|---:|---:|---:|---:|
| 1,150 / 4 | 7 | 250 | 6 | 1,000000 |
| 1,200 / 4 | 6 | 240 | 4 | 0,978125 |
| 1,175 / 3 | 11 | 225 | 19 | 0,999670 |
| 1,175 / 5 | 3 | 268 | 24 | 1,000000 |

La concentración principal cambia poco, pero los grupos pequeños aparecen, desaparecen o pasan a ruido: la cantidad de siete grupos no es robusta a estos cambios locales. Un ARI alto sobre alumnos comunes puede coexistir con cambios en grupos pequeños y exclusiones; por eso se informa junto con cobertura y tamaños.

La alternativa `0,5/10` sigue siendo sensible al radio: subirlo a `0,525` reduce los grupos de siete a cuatro, concentra 96,99 % de los agrupados en uno y produce ARI de 0,095679 sobre alumnos agrupados en ambas ejecuciones.

## Diagnóstico auxiliar al retirar deserto

Esta prueba responde únicamente a la duda de si `deserto` explica la concentración de DBSCAN. Por decisión del trabajo, **no forma parte de la comparación principal ni se utiliza para elegir su configuración final**. La comparación principal conserva los diez atributos originales y la misma entrada para los tres métodos.

Se conservaron los 2.587 alumnos, su orden y los valores estandarizados de los otros nueve atributos. Se retiró solo la columna `deserto`, sin filtros ni ajustes de escalado adicionales. El código de producción, sus esquemas y parámetros predeterminados no se modificaron.

Se ejecutaron cinco configuraciones fijas de DBSCAN con y sin esa columna, además del jerárquico Ward con corte a altura 35 y K-Means con k=7 y los parámetros existentes. No se realizó una nueva búsqueda de parámetros. `deserto` se conservó en los datos originales para describir los grupos, pero no intervino en la matriz de nueve atributos.

| eps / min_samples | Grupos, con y sin `deserto` | Ruido, con y sin `deserto` | Grupo mayor entre agrupados, con y sin `deserto` |
|---|---:|---:|---:|
| 1,5 / 5 | 1 | 194 (7,50 %) | 100,00 % |
| 1,1 / 10 | 3 | 313 (12,10 %) | 96,00 % |
| 0,5 / 10 | 7 | 749 (28,95 %) | 81,50 % |
| 0,5 / 6 | 14 | 632 (24,43 %) | 77,29 % |
| 1,175 / 4 | 7 | 244 (9,43 %) | 94,54 % |

Se verificó igualdad exacta de etiquetas por alumno, incluidos los alumnos marcados como ruido. ARI=1 en las cinco comparaciones. Los 74 alumnos con `deserto=0` siguieron como ruido en todos estos casos. Silhouette también coincide dentro de la precisión numérica.

Dentro de estas cinco configuraciones, la concentración persiste al retirar la columna: no puede atribuirse solamente a su inclusión. Esto no demuestra que `deserto` nunca afecte a DBSCAN con otros parámetros.

| Método | Con `deserto` | Sin `deserto` | ARI entre ambas asignaciones |
|---|---|---|---:|
| Jerárquico, Ward h=35 | 7 grupos; tamaños 903, 636, 355, 332, 236, 74, 51 | 6 grupos; tamaños 903, 636, 508, 350, 128, 62 | 0,936084 |
| K-Means, k=7 | 7 grupos; tamaños 1101, 506, 405, 326, 95, 81, 73 | 7 grupos; tamaños 1150, 507, 385, 332, 107, 59, 47 | 0,907459 |

El jerárquico se calculó directamente con SciPy usando el mismo enlace y altura, para observar la cantidad resultante sin la exigencia de siete grupos del módulo de producción. La ejecución de control con diez atributos coincide en asignaciones con la referencia actual. No se ajustó el corte para recuperar siete grupos.

La retirada de una variable sí puede modificar la estructura y las asignaciones. Su efecto depende del método y de los parámetros.

## Implementación y casos fijos actuales

`src.runs.dbscan.pruebas(entrada, directorio)` llama a `methods.dbscan.analizar` para la configuración individual y los cinco casos predeterminados. Genera los gráficos y muestra los perfiles y la tabla conjunta en consola. Devuelve `resultado` (la ejecución individual) y `casos` (una lista con `nombre`, `descripcion` y `resultado`). Si la configuración individual coincide con un caso fijo, reutiliza su resultado. `comparacion.main` delega en este run y conserva la lista de casos en `pruebas_dbscan`.

| Caso | eps / min_samples | Propósito | Resultado en 2026-10-01 |
|---|---|---|---|
| `referencia` | 1,5 / 5 | Configuración del R original | Un grupo; 7,50 % de ruido |
| `siete_poco_ruido` | 1,175 / 4 | Mostrar concentración pese a siete grupos y poco ruido | Siete grupos; 9,43 % de ruido; mayor 94,54 % de agrupados |
| `siete_mas_ruido` | 0,5 / 10 | Mostrar el costo de reducir esa concentración | Siete grupos; 28,95 % de ruido; mayor 81,50 % |
| `catorce_grupos` | 0,5 / 6 | Mostrar más grupos con concentración persistente | Catorce grupos; 24,43 % de ruido; mayor 77,29 % |
| `fragmentacion` | 0,18 / 5 | Mostrar fragmentación y exclusión con radio pequeño | 59 grupos; 45,84 % de ruido; mayor 38,83 % |

Son casos ilustrativos seleccionados a partir de las exploraciones, no una nueva búsqueda ni una validación independiente. Los nombres describen resultados en la fecha de referencia; no garantizan esas cantidades al cambiar la fecha o los datos. Todos reciben los diez atributos originales, incluido `deserto`. El diagnóstico que lo retira permanece separado.

Cada caso genera los gráficos habituales en `output/dbscan/experimentos/<caso>/graficos/`. La figura `output/dbscan/experimentos/graficos/comparacion.png` resume cantidad de grupos, porcentaje de ruido y proporción del grupo mayor entre alumnos agrupados. No se agregan exportaciones automáticas de CSV ni evaluaciones ARI al flujo principal.

## Antecedente de la configuración inicial

`Legacy/scripts/script_extra.R` ya ejecutaba DBSCAN sobre `alumnos_s_avanzados_sc`, con `eps=1.5` y `minPts=5` (líneas 27 y 55), y excluía ruido antes de calcular Silhouette. Es una configuración fija, no una exploración de parámetros. No hay resultados de esa ejecución R guardados junto al script que permitan establecer qué partición obtuvieron sus autores. El comentario sobre valores faltantes antes de K-Means no demuestra que el script nunca se haya ejecutado.

El notebook `Legacy/migracion_inicial/03_analisis_extra.ipynb` sí conserva salidas de una ejecución de la migración a Python: DBSCAN produjo un grupo con 2.393 observaciones sin ruido y Silhouette no disponible. Ese registro es evidencia de la migración, no una salida histórica de R.

## Decisión final y límites

La búsqueda se cerró sin adoptar DBSCAN como segmentación académica seleccionada. Las configuraciones de mayor cobertura reúnen a la mayoría en un grupo dominante; reducir esa concentración introduce fragmentación y ruido elevado. Obtener siete etiquetas o aumentar Silhouette no basta para justificar perfiles útiles. Esta conclusión corresponde a la entrada, distancia y configuraciones estudiadas y no demuestra una imposibilidad general.

Los parámetros predeterminados `eps=1.5` y `min_samples=5` se conservan como referencia del antecedente original, no como una solución seleccionada. Las búsquedas, ARI, pruebas de orden y diagnóstico sin `deserto` no se ejecutan desde `main.py`.

## Reproducción y respaldo local

Los casos fijos se ejecutan desde la raíz con `uv run python main.py --fecha 2026-10-01`. Los parámetros `--eps` y `--min-samples` cambian la ejecución individual, sin alterar los cinco casos. La ejecución imprime resúmenes y guarda gráficos; no exporta las tablas completas de las búsquedas históricas.

Los registros originales sitúan scripts, versiones, huellas, asignaciones, perfiles y tablas de sensibilidad en estas carpetas locales:

| Registro | Carpeta |
|---|---|
| Primera exploración | `output/dbscan/experimentos/dbscan_2026-10-01/` |
| Ampliación y PCA | `output/dbscan/experimentos/dbscan_ampliacion_2026-10-01/` |
| Grilla y concordancia | `output/dbscan/experimentos/dbscan_concordancia_2026-10-01/` |
| Diagnóstico sin deserto | `output/dbscan/experimentos/diagnostico_sin_deserto_2026-10-01/` |

`output/` está excluido de Git: esos artefactos no se distribuyen al clonar el repositorio. Este anexo conserva el protocolo y los resultados registrados, pero el código versionado sólo reproduce directamente los cinco casos fijos. La verificación R–Python tiene su propio registro de evidencia.

## Referencias

- [Informe final de la experiencia](experiencia-dbscan.pdf) y [fuente editable](experiencia-dbscan.docx).
- [Método DBSCAN](../../src/methods/dbscan.py), [ejecución y casos](../../src/runs/dbscan.py) y [flujo de archivos](../flujos/flujo-archivos.md).
- [Guía de clustering de scikit-learn](https://scikit-learn.org/stable/modules/clustering.html), [DBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html) y [PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html).
