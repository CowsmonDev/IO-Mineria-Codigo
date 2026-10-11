# K-Means: ejecución principal y antecedentes

## Propósito y estado actual

K-Means genera una agrupación propia sobre los mismos alumnos y atributos que recibe el jerárquico. La pregunta es cómo cambian los integrantes y las características de los grupos. Los siete grupos actuales se fijaron para comparar una partición con la misma cantidad que la referencia; no se impone que sus miembros coincidan.

La ejecución actual conserva k=7, k-means++, 25 inicializaciones, semilla 123 y los resultados principales de esta nota. Muestra resúmenes y genera gráficos individuales. Las correspondencias, ARI y repeticiones descritas más abajo pertenecen a la primera implementación y no se calculan automáticamente en el flujo actual.

La referencia jerárquica aquí usada es la ejecución reproducible con fecha `2026-10-01`, cuya equivalencia con R está verificada. Reproducir las cifras o la fecha de los PDF no es un requisito. Ver [criterios del trabajo](../criterios-del-trabajo.md#equivalencia-rpython-y-referencia-de-trabajo).

## Registro histórico de la primera comparación

Ejecución realizada el 4 de octubre de 2026, con fecha de análisis fijada al 1 de octubre de 2026 para conservar la entrada de la verificación de la migración.

## Entrada y protocolo

Se utilizaron 2.587 estudiantes y las siguientes diez variables, en este orden: `tiempo_desde_ingreso`, `cursadas_aprobadas`, `cursadas_promocionadas`, `cursadas_desaprobadas`, `materias_anotado_ult_anio`, `finales_aprobados`, `finales_desaprobados`, `dias_dsd_ultimo_final`, `porc_finales` y `deserto`.

La matriz se contrastó con `output/comparacion_r_2026-10-01/r/datos_estandarizados.csv`: contiene el mismo multiconjunto de filas, con diferencias numéricas inferiores a 1e-9. El orden de algunas filas difiere entre R y Python; en esta comparación ambos métodos usan el mismo orden de Python y se conserva el identificador por fila.

Se conservó la estandarización con desvío muestral (`ddof=1`). Las etiquetas jerárquicas y los identificadores no integraron la matriz de entrada. `deserto` sí integra la entrada, como en el estudio original; los porcentajes de deserción de los grupos no son una evaluación independiente ni una medida predictiva.

K-Means: siete grupos, inicialización `k-means++`, 25 inicializaciones por ejecución, Lloyd, máximo de 300 iteraciones y tolerancia 0,0001. La semilla principal es 123, fijada antes de interpretar los resultados. Se realizaron otras nueve ejecuciones con semillas 0 a 8. Cada ejecución conserva el resultado de menor inercia entre sus 25 inicializaciones.

## Resultados iniciales

| Método | Grupos | Estudiantes evaluados | Silhouette | Inercia K-Means | ARI contra jerárquico |
|---|---:|---:|---:|---:|---:|
| Jerárquico | 7 | 2.587 | 0,295444 | No aplica | 1 |
| K-Means, semilla 123 | 7 | 2.587 | 0,365474 | 6.850,871199 | 0,670893 |

Silhouette se calculó con distancia euclídea sobre toda la población en ambos métodos. El valor de la referencia coincide con el registrado durante la comparación con R. ARI cuantifica concordancia de integrantes sin depender de los números de las etiquetas; no expresa el porcentaje de estudiantes coincidentes ni indica que el jerárquico sea una clasificación verdadera.

| Grupo (etiquetas independientes) | Tamaño jerárquico | Tamaño K-Means |
|---|---:|---:|
| 1 | 51 | 506 |
| 2 | 332 | 1.101 |
| 3 | 236 | 73 |
| 4 | 74 | 326 |
| 5 | 355 | 95 |
| 6 | 903 | 405 |
| 7 | 636 | 81 |

Las columnas de tamaños no implican una correspondencia entre grupos. La primera implementación exportaba tablas y mapas de calor para consultarla; el flujo actual no los genera. La nueva comparación deberá estudiar esa correspondencia e interpretar los perfiles, sin depender del número de etiqueta.

## Estabilidad y límites de interpretación

El ARI mínimo entre pares de semillas fue 0,666514. Las inercias variaron entre 6.849,220212 y 6.875,447692; los Silhouette, entre 0,365474 y 0,446351. Ninguna ejecución alcanzó el límite de 300 iteraciones.

La semilla 6 produjo la mayor inercia y el mayor Silhouette del conjunto, mostrando que ambos criterios pueden favorecer resultados distintos. Se conserva la semilla principal prefijada y se informa esta variación. Todavía corresponde interpretar la composición y los perfiles, y estudiar si aumentar las inicializaciones mejora la estabilidad antes de extraer conclusiones definitivas. Estas repeticiones examinan sensibilidad a la inicialización, no estabilidad frente a cambios de muestra.

## Reproducción y archivos

```bash
uv run python main.py --fecha 2026-10-01
```

Esta nota documenta la primera implementación, que generó tablas en `output/kmeans/` y gráficos en `output/graficos/kmeans/`. Las métricas de correspondencia y estabilidad descritas arriba pertenecen a esa ejecución histórica. La ejecución actual conserva el agrupamiento principal, muestra sus resultados básicos en consola y genera PNG en `output/<método>/graficos/`; no ejecuta la comparación ni exporta tablas. El [README](../../README.md) describe el alcance actual.
