# Comparación de agrupamientos de estudiantes mediante clustering jerárquico, K-Means y DBSCAN

**Trabajo final de Investigación Operativa — Facultad de Ciencias Exactas, UNICEN**

Autor: [Completar]. Profesor: [Completar]. Fecha de presentación: [Completar].

> Borrador de trabajo actualizado el 11 de octubre de 2026. El informe final de DBSCAN y su anexo técnico registran el cierre de esa exploración. Se distinguen los resultados publicados, las ejecuciones actuales y los análisis pendientes. No se presentan conclusiones comparativas definitivas.

## 1. Antecedentes y pregunta de investigación

Clementi y Salias estudiaron la deserción en Ingeniería de Sistemas mediante datos académicos del SIU Guaraní, regresión logística penalizada LASSO y clustering jerárquico. El jerárquico permitió describir perfiles a partir del avance académico, permanencia, actividad y deserción.

En trabajos futuros propusieron enriquecer los datos con indicadores socioeconómicos y contextuales y aplicar K-Means y DBSCAN para contrastar los perfiles hallados. Esta extensión retoma la comparación de agrupamientos sobre la base académica existente.

La pregunta es: **¿cómo cambia la agrupación de los mismos estudiantes al aplicar K-Means y DBSCAN sobre los mismos atributos usados por el jerárquico?**

## 2. Objetivo y alcance

### Objetivo general

Comparar cómo cambia la agrupación de los mismos estudiantes al aplicar K-Means y DBSCAN sobre la misma entrada académica utilizada por el clustering jerárquico, analizando la cantidad de grupos, sus integrantes y sus características académicas.

### Objetivos específicos

1. Establecer una entrada común reproducible y verificar la equivalencia del jerárquico en R y Python.
2. Obtener asignaciones independientes mediante los tres métodos.
3. Comparar cantidad, tamaños, cobertura y separación de los grupos.
4. Analizar qué alumnos permanecen juntos y qué perfiles se dividen, se fusionan o aparecen como ruido.
5. Examinar la sensibilidad de K-Means a la inicialización y de DBSCAN a sus parámetros.

Los nuevos métodos se aplican a los atributos, no a los clusters producidos por el jerárquico. La referencia jerárquica permite estudiar diferencias; sus etiquetas no se consideran verdaderas clases.

Se conserva LASSO como antecedente separado. Sus coeficientes no seleccionan ni ponderan atributos del clustering. El enriquecimiento socioeconómico, la predicción supervisada y la aplicación institucional de alertas quedan fuera del alcance actual.

## 3. Entrada común

### Población y preparación

Se utilizan cuatro CSV de estudiantes, regularidades, historia académica y materias de planes. El procesamiento selecciona Ingeniería de Sistemas, con fecha de inscripción posterior a `2011-01-01` y anterior a `2023-12-31`, excluye egresados y un alumno de intercambio, aplica los filtros originales y conserva la población con `porc_finales <= 0.5`.

La entrada actual con fecha de análisis `2026-10-01` contiene 2.587 alumnos. `prepare_input` carga los datos mediante `prepare_academic_data`, conserva sus identificadores por separado y construye dos tablas alineadas por posición: valores originales y valores estandarizados.

### Atributos

El orden de las diez columnas es el siguiente. Todas se almacenan como `float64` después de la preparación.

| Atributo | Significado en la implementación | Unidad original |
|---|---|---|
| `tiempo_desde_ingreso` | Tiempo entre inscripción y fecha de análisis. | Días |
| `cursadas_aprobadas` | Cursadas aprobadas según los registros y ajustes por cambio de plan del original. | Conteo |
| `cursadas_promocionadas` | Cursadas aprobadas con condición de promoción. | Conteo |
| `cursadas_desaprobadas` | Registros reprobados o ausentes, con ajustes por cambio de plan del original. | Conteo |
| `materias_anotado_ult_anio` | Materias distintas registradas en regularidades de 2023. | Conteo |
| `finales_aprobados` | Registros de finales aprobados. | Conteo |
| `finales_desaprobados` | Registros de finales reprobados o ausentes. | Conteo |
| `dias_dsd_ultimo_final` | Tiempo desde el último final; sin finales, desde la inscripción. | Días |
| `porc_finales` | Finales aprobados divididos por la cantidad de materias del plan según los filtros originales. | Proporción |
| `deserto` | Condición de deserción calculada por el procesamiento original. | 0 o 1 |

En la población filtrada, `deserto` se define por más de 730 días desde el último final y ausencia de materias registradas en 2023, o por calidad administrativa «Abandono». El año 2023 es fijo en el procesamiento; cambiar la fecha de análisis no desplaza ese período.

Cada columna se estandariza restando su media y dividiendo por su desvío muestral (`ddof=1`). Los esquemas Pandera declaran columnas, orden y tipos; se comprueban nulos, identidad, alineación y valores finitos. Los identificadores y las etiquetas de agrupamiento no integran la matriz.

`deserto` sí integra la matriz, como en el código original. Por ello, su distribución por grupo es descriptiva y no constituye validación independiente de predicción de abandono.

## 4. Métodos y output

El output principal es una etiqueta por alumno. A partir de esa asignación se calculan cantidades, medias y distribuciones por grupo en unidades originales.

| Método | Criterio de agrupamiento | Cantidad de grupos | Información adicional |
|---|---|---|---|
| Jerárquico | Distancias euclídeas, enlace Ward y corte del árbol. | El corte actual h=35 produce siete; el código exige esa cantidad. | Árbol, dendrogramas y Silhouette para k=2 a 15. |
| K-Means | Agrupamiento alrededor de centros minimizando distancias euclídeas cuadradas. | Fijada en siete en la configuración actual. | Centros e inercia. |
| DBSCAN | Regiones conectadas por densidad con vecindades euclídeas. | Surge de `eps` y `min_samples`; puede ser distinta de siete. | Ruido y distancias de vecinos. |

K-Means usa k-means++, 25 inicializaciones, semilla 123, Lloyd, máximo 300 iteraciones y tolerancia 0,0001. DBSCAN usa inicialmente `eps=1.5` y `min_samples=5`, incluyendo al propio punto. La exploración de DBSCAN está cerrada: no se adoptó una configuración como segmentación seleccionada; la implementación y sus casos se conservan como evidencia.

Los grupos se numeran independientemente. El grupo 1 de K-Means no equivale al grupo 1 jerárquico. DBSCAN identifica ruido con `-1`; esa categoría no es un perfil homogéneo por definición.

## 5. Comparación prevista

### Asignaciones y perfiles

Se cruzarán las asignaciones del jerárquico con las de cada método alternativo, incluyendo ruido para DBSCAN. Las tablas permitirán estudiar si los integrantes de un grupo permanecen juntos, se reparten entre varios grupos o se reúnen con integrantes de otros.

Se interpretarán las correspondencias mediante cantidades, proporciones, medias y distribuciones de los atributos. ARI puede complementar la concordancia de asignaciones, sin interpretarse como exactitud o porcentaje de coincidencia.

### Separación y cobertura

Silhouette compara la distancia media de cada alumno a su grupo con la distancia media al otro grupo más cercano. Valores próximos a 1 indican separación; próximos a 0, frontera; negativos, mayor cercanía media a otro grupo. Su promedio resume esa geometría, no la utilidad institucional del perfil.

Se requiere entre dos y n−1 grupos. DBSCAN excluye ruido en la implementación actual; se informa la cantidad de alumnos evaluados. Para contrastar sobre la misma población se puede recalcular Silhouette de los otros métodos sobre esos alumnos, manteniendo sus asignaciones y comprobando que el cálculo sea válido. Silhouette favorece grupos compactos y convexos, por lo que no será el único criterio para valorar DBSCAN.

### Sensibilidad

Queda por examinar la inicialización de K-Means; las configuraciones cercanas de DBSCAN ya se estudiaron en sus exploraciones registradas. Coincidencia entre métodos y sensibilidad dentro de un método se analizarán por separado. La selección de parámetros considerará cantidad de grupos, cobertura, separación e interpretación de perfiles; no exigirá siete grupos para DBSCAN.

Estas comparaciones están previstas, pero la ejecución actual no las realiza automáticamente.

## 6. Resultados y estado de la referencia

### Resultados publicados

Los PDF presentan siete grupos jerárquicos y Silhouette aproximado de 0,40. Desarrollan principalmente los siguientes perfiles:

| Perfil según los autores | Rasgos publicados |
|---|---|
| Cluster 1: rezagados y en riesgo de deserción | Antigüedad elevada, muchas desaprobaciones, inactividad prolongada y 93,8 % de deserción. |
| Cluster 4: trayectoria sólida y mayor avance relativo | Más aprobaciones y promociones; 11,4 % de deserción. |
| Cluster 7: progreso regular | Menor antigüedad, buen desempeño en finales y 0 % de deserción. |

Estas descripciones se conservan como antecedentes interpretativos. Reproducir sus cifras o la fecha de la publicación no es un requisito del proyecto; la comparación se realiza sobre la entrada común fijada.

### Ejecución reproducible actual

| Método | Grupos | Alumnos agrupados | Ruido | Silhouette | Alumnos evaluados para Silhouette |
|---|---:|---:|---:|---:|---:|
| Jerárquico | 7 | 2.587 | 0 | 0,295444 | 2.587 |
| K-Means | 7 | 2.587 | 0 | 0,365474 | 2.587 |
| DBSCAN, eps=1,5; min_samples=5 | 1 | 2.393 | 194 | No calculable | 0; hay 2.393 alumnos sin ruido |

Los resultados corresponden a la entrada fechada `2026-10-01`. K-Means presenta mayor Silhouette que el jerárquico en esta ejecución; falta analizar la composición y significado de los perfiles. La configuración original de DBSCAN identifica una región densa y ruido. Las exploraciones posteriores cerraron su evaluación sin adoptarlo como segmentación seleccionada.

El [informe final de DBSCAN](../resultados/experiencia-dbscan.pdf) y su [anexo técnico](../resultados/anexo-tecnico-dbscan.md) detallan el registro disponible. El antecedente de K-Means se conserva en el anexo de este borrador. Las métricas históricas de concordancia y repeticiones de K-Means no se calculan en la ejecución actual.

### Equivalencia de la migración y referencia aceptada

Se comprobó R frente a Python con los mismos CSV y cinco fechas de análisis. En todas coinciden los alumnos y atributos, el agrupamiento alineado por ID (ARI=1) y Silhouette dentro de la precisión numérica. La diferencia máxima observada entre matrices estandarizadas fue inferior a 4e-14. Ver [verificación R–Python](../resultados/verificacion-fechas-r-python.md).

La referencia aceptada es el jerárquico de Python sobre la entrada fijada en `2026-10-01`. El requisito es la equivalencia con el procedimiento R sobre esa misma entrada, no reconstruir la fecha y las cifras del PDF. La investigación de diferencias con la publicación queda cerrada y no constituye una limitación pendiente de resolver para continuar el proyecto.

## 7. Salidas y evidencia que debe producir el código

Actualmente se muestran parámetros, resúmenes y Silhouette en consola. Los resultados quedan en memoria al llamar a `main()` y los gráficos se guardan en `output/<método>/graficos/`, con el nombre de carpeta `k-means` para K-Means.

El jerárquico guarda además `resumen_clusters.csv` y dendrogramas internos y zooms en PDF. K-Means y DBSCAN guardan PNG. Los dendrogramas internos corresponden a análisis del jerárquico; los boxplots, tamaños y perfiles permiten inspeccionar los tres métodos.

La siguiente evidencia comparativa prevista es una tabla cruzada de asignaciones y la interpretación de perfiles en unidades originales. El anexo técnico de DBSCAN conserva sus configuraciones y pruebas de sensibilidad; esas búsquedas no se ejecutan automáticamente. Ver [flujo por archivos](../flujos/flujo-archivos.md).

## 8. Discusión y conclusiones pendientes

La discusión deberá responder qué diferencias se observan en cantidad e integrantes de los grupos, qué perfiles académicos se conservan o cambian, qué trayectorias quedan como ruido y cuánto dependen los resultados de la configuración.

Se distinguirán asociaciones descriptivas de causas de abandono y de capacidad predictiva. No se concluirá que un algoritmo es mejor únicamente por Silhouette o por su coincidencia con el jerárquico.

La referencia R–Python está verificada y la evaluación de DBSCAN está cerrada. Su conclusión y sus límites constan en el informe final. Queda pendiente completar la comparación de perfiles con los otros métodos.

## 9. Fuentes

- Clementi, G. y Salias, L. G. (2025). [Informe de Trabajo Final de Investigación Operativa](IO-Mineria-Informe-Clementi-Salias.pdf), secciones 3.2.1, 4.3 y 5.
- [Analyzing students dropout using penalized logistic regression and hierarchical clustering: a case study in systems engineering](<Analyzing students dropout using penalized logistic regression and hierarchical clustering a case study in systems engineering.docx.pdf>), secciones 3, 4.4 y 5.
- [Código original R](../../Legacy/scripts) y [preparación actual](../../src/data/preparation.py).
- [Documentación de clustering de scikit-learn](https://scikit-learn.org/stable/modules/clustering.html).


## Anexo histórico de K-Means

### Propósito y estado actual

K-Means genera una agrupación propia sobre los mismos alumnos y atributos que recibe el jerárquico. La pregunta es cómo cambian los integrantes y las características de los grupos. Los siete grupos actuales se fijaron para comparar una partición con la misma cantidad que la referencia; no se impone que sus miembros coincidan.

La ejecución actual conserva k=7, k-means++, 25 inicializaciones, semilla 123 y los resultados principales de esta nota. Muestra resúmenes y genera gráficos individuales. Las correspondencias, ARI y repeticiones descritas más abajo pertenecen a la primera implementación y no se calculan automáticamente en el flujo actual.

La referencia jerárquica aquí usada es la ejecución reproducible con fecha `2026-10-01`, cuya equivalencia con R está verificada. Reproducir las cifras o la fecha de los PDF no es un requisito. Ver [criterios del trabajo](../criterios-del-trabajo.md#equivalencia-rpython-y-referencia-de-trabajo).

### Registro histórico de la primera comparación

Ejecución realizada el 4 de octubre de 2026, con fecha de análisis fijada al 1 de octubre de 2026 para conservar la entrada de la verificación de la migración.

### Entrada y protocolo

Se utilizaron 2.587 estudiantes y las siguientes diez variables, en este orden: `tiempo_desde_ingreso`, `cursadas_aprobadas`, `cursadas_promocionadas`, `cursadas_desaprobadas`, `materias_anotado_ult_anio`, `finales_aprobados`, `finales_desaprobados`, `dias_dsd_ultimo_final`, `porc_finales` y `deserto`.

La matriz se contrastó con `output/comparacion_r_2026-10-01/r/datos_estandarizados.csv`: contiene el mismo multiconjunto de filas, con diferencias numéricas inferiores a 1e-9. El orden de algunas filas difiere entre R y Python; en esta comparación ambos métodos usan el mismo orden de Python y se conserva el identificador por fila.

Se conservó la estandarización con desvío muestral (`ddof=1`). Las etiquetas jerárquicas y los identificadores no integraron la matriz de entrada. `deserto` sí integra la entrada, como en el estudio original; los porcentajes de deserción de los grupos no son una evaluación independiente ni una medida predictiva.

K-Means: siete grupos, inicialización `k-means++`, 25 inicializaciones por ejecución, Lloyd, máximo de 300 iteraciones y tolerancia 0,0001. La semilla principal es 123, fijada antes de interpretar los resultados. Se realizaron otras nueve ejecuciones con semillas 0 a 8. Cada ejecución conserva el resultado de menor inercia entre sus 25 inicializaciones.

### Resultados iniciales

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

### Estabilidad y límites de interpretación

El ARI mínimo entre pares de semillas fue 0,666514. Las inercias variaron entre 6.849,220212 y 6.875,447692; los Silhouette, entre 0,365474 y 0,446351. Ninguna ejecución alcanzó el límite de 300 iteraciones.

La semilla 6 produjo la mayor inercia y el mayor Silhouette del conjunto, mostrando que ambos criterios pueden favorecer resultados distintos. Se conserva la semilla principal prefijada y se informa esta variación. Todavía corresponde interpretar la composición y los perfiles, y estudiar si aumentar las inicializaciones mejora la estabilidad antes de extraer conclusiones definitivas. Estas repeticiones examinan sensibilidad a la inicialización, no estabilidad frente a cambios de muestra.

### Reproducción y archivos

```bash
uv run python main.py --date 2026-10-01
```

Esta nota documenta la primera implementación, que generó tablas en `output/kmeans/` y gráficos en `output/graficos/kmeans/`. Las métricas de correspondencia y estabilidad descritas arriba pertenecen a esa ejecución histórica. La ejecución actual conserva el agrupamiento principal, muestra sus resultados básicos en consola y genera PNG en `output/<método>/graficos/`; no ejecuta la comparación ni exporta tablas. El [README](../../README.md) describe el alcance actual.
