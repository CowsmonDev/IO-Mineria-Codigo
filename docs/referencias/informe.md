# Comparación de agrupamientos de estudiantes mediante clustering jerárquico, K-Means y DBSCAN

**Trabajo final de Investigación Operativa — Facultad de Ciencias Exactas, UNICEN**

Autor: [Completar]. Profesor: [Completar]. Fecha de presentación: [Completar].

> Borrador de trabajo actualizado el 5 de octubre de 2026. Se distinguen los resultados publicados, las ejecuciones actuales y los análisis pendientes. No se presentan conclusiones comparativas definitivas.

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

La entrada actual con fecha de análisis `2026-10-01` contiene 2.587 alumnos. `preparar_entrada` carga los datos mediante `preparar_datos_academicos`, conserva sus identificadores por separado y construye dos tablas alineadas por posición: valores originales y valores estandarizados.

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

K-Means usa k-means++, 25 inicializaciones, semilla 123, Lloyd, máximo 300 iteraciones y tolerancia 0,0001. DBSCAN usa inicialmente `eps=1.5` y `min_samples=5`, incluyendo al propio punto. La elección final de parámetros de DBSCAN queda pendiente.

Los grupos se numeran independientemente. El grupo 1 de K-Means no equivale al grupo 1 jerárquico. DBSCAN identifica ruido con `-1`; esa categoría no es un perfil homogéneo por definición.

## 5. Comparación prevista

### Asignaciones y perfiles

Se cruzarán las asignaciones del jerárquico con las de cada método alternativo, incluyendo ruido para DBSCAN. Las tablas permitirán estudiar si los integrantes de un grupo permanecen juntos, se reparten entre varios grupos o se reúnen con integrantes de otros.

Se interpretarán las correspondencias mediante cantidades, proporciones, medias y distribuciones de los atributos. ARI puede complementar la concordancia de asignaciones, sin interpretarse como exactitud o porcentaje de coincidencia.

### Separación y cobertura

Silhouette compara la distancia media de cada alumno a su grupo con la distancia media al otro grupo más cercano. Valores próximos a 1 indican separación; próximos a 0, frontera; negativos, mayor cercanía media a otro grupo. Su promedio resume esa geometría, no la utilidad institucional del perfil.

Se requiere entre dos y n−1 grupos. DBSCAN excluye ruido en la implementación actual; se informa la cantidad de alumnos evaluados. Para contrastar sobre la misma población se puede recalcular Silhouette de los otros métodos sobre esos alumnos, manteniendo sus asignaciones y comprobando que el cálculo sea válido. Silhouette favorece grupos compactos y convexos, por lo que no será el único criterio para valorar DBSCAN.

### Sensibilidad

Se examinarán inicializaciones adicionales de K-Means y configuraciones cercanas de DBSCAN. Coincidencia entre métodos y sensibilidad dentro de un método se analizarán por separado. La selección de parámetros considerará cantidad de grupos, cobertura, separación e interpretación de perfiles; no exigirá siete grupos para DBSCAN.

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

Los resultados corresponden a la entrada fechada `2026-10-01`. K-Means presenta mayor Silhouette que el jerárquico en esta ejecución; falta analizar la composición y significado de los perfiles. DBSCAN identifica una región densa y ruido; falta explorar y justificar parámetros antes de definir su configuración final.

Las notas [K-Means](../resultados/resultados-kmeans.md) y [DBSCAN](../resultados/resultados-dbscan.md) detallan el registro disponible. Las métricas históricas de concordancia y repeticiones de K-Means no se calculan en la ejecución actual.

### Equivalencia de la migración y referencia aceptada

Se comprobó R frente a Python con los mismos CSV y cinco fechas de análisis. En todas coinciden los alumnos y atributos, el agrupamiento alineado por ID (ARI=1) y Silhouette dentro de la precisión numérica. La diferencia máxima observada entre matrices estandarizadas fue inferior a 4e-14. Ver [verificación R–Python](../resultados/verificacion-fechas-r-python.md).

La referencia aceptada es el jerárquico de Python sobre la entrada fijada en `2026-10-01`. El requisito es la equivalencia con el procedimiento R sobre esa misma entrada, no reconstruir la fecha y las cifras del PDF. La investigación de diferencias con la publicación queda cerrada y no constituye una limitación pendiente de resolver para continuar el proyecto.

## 7. Salidas y evidencia que debe producir el código

Actualmente se muestran parámetros, resúmenes y Silhouette en consola. Los resultados quedan en memoria al llamar a `main()` y los gráficos se guardan en `output/<método>/graficos/`, con el nombre de carpeta `k-means` para K-Means.

El jerárquico guarda además `resumen_clusters.csv` y dendrogramas internos y zooms en PDF. K-Means y DBSCAN guardan PNG. Los dendrogramas internos corresponden a análisis del jerárquico; los boxplots, tamaños y perfiles permiten inspeccionar los tres métodos.

La siguiente evidencia comparativa prevista es una tabla cruzada de asignaciones y la interpretación de perfiles en unidades originales. El registro de configuraciones y sensibilidad se definirá en una etapa posterior. Ver [flujo por archivos](../flujos/flujo-archivos.md).

## 8. Discusión y conclusiones pendientes

La discusión deberá responder qué diferencias se observan en cantidad e integrantes de los grupos, qué perfiles académicos se conservan o cambian, qué trayectorias quedan como ruido y cuánto dependen los resultados de la configuración.

Se distinguirán asociaciones descriptivas de causas de abandono y de capacidad predictiva. No se concluirá que un algoritmo es mejor únicamente por Silhouette o por su coincidencia con el jerárquico.

[Completar las conclusiones cuando se haya aclarado la referencia y realizado la comparación de asignaciones y perfiles.]

## 9. Fuentes

- Clementi, G. y Salias, L. G. (2025). [Informe de Trabajo Final de Investigación Operativa](IO-Mineria-Informe-Clementi-Salias.pdf), secciones 3.2.1, 4.3 y 5.
- [Analyzing students dropout using penalized logistic regression and hierarchical clustering: a case study in systems engineering](<Analyzing students dropout using penalized logistic regression and hierarchical clustering a case study in systems engineering.docx.pdf>), secciones 3, 4.4 y 5.
- [Código original R](../../Legacy/scripts) y [preparación actual](../../src/data/preparacion.py).
- [Documentación de clustering de scikit-learn](https://scikit-learn.org/stable/modules/clustering.html).
