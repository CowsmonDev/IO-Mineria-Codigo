# DBSCAN: configuración inicial y resultados

## Propósito

DBSCAN produce una asignación propia de los mismos alumnos y atributos que recibe el jerárquico. La comparación estudiará qué alumnos quedan juntos, qué perfiles se reúnen o se separan y cuáles quedan como ruido. La cantidad de grupos surge de la densidad; no se exige que coincida con los siete del jerárquico.

## Entrada y configuración

La ejecución actual utiliza 2.587 alumnos, diez atributos y fecha de análisis `2026-10-01`, con estandarización muestral. Parámetros iniciales: `eps=1.5`, `min_samples=5` y distancia euclídea. Los valores retoman el antecedente de código y no constituyen todavía una elección final justificada.

`eps` define el radio de vecindad. `min_samples` exige una cantidad mínima de puntos en ese radio para que un alumno sea núcleo, incluido él mismo. Los grupos se expanden mediante conexiones de puntos núcleo; su diámetro puede superar `eps`.

## Resultado observado

- Un grupo de 2.393 alumnos.
- 194 alumnos como ruido: 7,4990 % de la población.
- Silhouette sin ruido no calculable porque queda un único grupo.

Ruido significa que esos alumnos no quedaron integrados en las regiones densas bajo esta configuración. No implica error en los datos ni que compartan un mismo perfil académico.

El resultado permite estudiar una región densa frente a trayectorias menos frecuentes, aunque todavía no ofrece varios grupos para contrastar perfiles. Debe analizarse de qué grupos jerárquicos provienen los alumnos agrupados y los casos de ruido; esa tabla está pendiente.

## Exploración realizada y elección pendiente

La referencia jerárquica Python está validada frente a R sobre la misma entrada; reproducir las cifras publicadas no es un requisito. Ver [criterios del trabajo](../criterios-del-trabajo.md#equivalencia-rpython-y-referencia-de-trabajo).

Se inspeccionó `vecinos.png` y se probaron dieciséis configuraciones explícitas; ver [exploración de DBSCAN](exploracion-dbscan.md). Los resultados mantienen una región dominante y varios grupos pequeños, con Silhouette bajo y cobertura variable. La configuración final no fue seleccionada. Con min_samples=5, el gráfico representa la distancia al cuarto vecino externo, pues el propio alumno ocupa una posición. Si se cambia min_samples, se recalcula la curva correspondiente.

Para cada configuración se registraron grupos, tamaños, cobertura, ruido, Silhouette cuando fue válido y características académicas. La elección se justificará por interpretación y sensibilidad además de separación. Maximizar Silhouette sobre pocos alumnos o buscar siete grupos no basta para responder al objetivo.

## Ejecución y salidas actuales

```bash
uv run python main.py
uv run python main.py --eps 0.8 --min-samples 10 --salida output/dbscan/experimentos/dbscan_0_8_10
```

El segundo comando es un ejemplo exploratorio y ejecuta los tres métodos. Los gráficos de DBSCAN incluyen vecinos, tamaños, boxplots, proporción de deserción y Silhouette o su motivo de indisponibilidad. Se guardan en `output/dbscan/graficos/`, o bajo la raíz indicada con `--salida`.

Los resúmenes se muestran en consola y quedan en memoria. La ejecución no selecciona parámetros automáticamente ni exporta tablas comparativas.

## Interpretación y límites

Silhouette excluye ruido; se debe informar la población incluida y considerar una comparación de los otros métodos sobre ese mismo subconjunto. La misma cobertura no elimina las limitaciones geométricas de Silhouette para grupos por densidad.

`deserto` participa como atributo. Su proporción dentro de los grupos es descriptiva, no una evaluación predictiva independiente.

Referencia metodológica: [DBSCAN en scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html).

## Búsqueda posterior de siete grupos

La [búsqueda acotada de concordancia](concordancia-dbscan.md) probó 470 configuraciones sobre la misma entrada. Ocho producen siete grupos con hasta 15 % de ruido, pero todas concentran al menos 94,54 % de los alumnos agrupados en uno. No se seleccionó una nueva configuración final. Las pruebas se guardan en `output/dbscan/experimentos/`.

## Casos fijos integrados en `main`

`dbscan.pruebas(matriz, originales)` llama a `analizar` para cinco configuraciones predeterminadas y devuelve una lista de casos con `nombre`, `descripcion` y `resultado`. `main` conserva su ejecución individual de DBSCAN, ejecuta esta lista, imprime los perfiles y una tabla conjunta, y devuelve la lista en `pruebas_dbscan`.

| Caso | eps / min_samples | Propósito | Resultado en 2026-10-01 |
|---|---|---|---|
| `referencia` | 1,5 / 5 | Configuración del R original | Un grupo; 7,50 % de ruido |
| `siete_poco_ruido` | 1,175 / 4 | Mostrar concentración pese a siete grupos y poco ruido | Siete grupos; 9,43 % de ruido; mayor 94,54 % de agrupados |
| `siete_mas_ruido` | 0,5 / 10 | Mostrar el costo de reducir esa concentración | Siete grupos; 28,95 % de ruido; mayor 81,50 % |
| `catorce_grupos` | 0,5 / 6 | Mostrar más grupos con concentración persistente | Catorce grupos; 24,43 % de ruido; mayor 77,29 % |
| `fragmentacion` | 0,18 / 5 | Mostrar fragmentación y exclusión con radio pequeño | 59 grupos; 45,84 % de ruido; mayor 38,83 % |

Son casos ilustrativos seleccionados a partir de las exploraciones, no una nueva búsqueda ni una validación independiente. Los nombres describen resultados en la fecha de referencia; no garantizan esas cantidades al cambiar la fecha o los datos. Todos reciben los diez atributos originales, incluido `deserto`. El diagnóstico que lo retira permanece separado.

Cada caso genera los gráficos habituales en `output/dbscan/experimentos/<caso>/graficos/`. La figura `output/dbscan/experimentos/graficos/comparacion.png` resume cantidad de grupos, porcentaje de ruido y proporción del grupo mayor entre alumnos agrupados. No se agregan exportaciones automáticas de CSV ni evaluaciones ARI al flujo principal.

### Antecedente en R

`Legacy/scripts/script_extra.R` ya ejecutaba DBSCAN sobre `alumnos_s_avanzados_sc`, con `eps=1.5` y `minPts=5` (líneas 27 y 55), y excluía ruido antes de calcular Silhouette. Es una configuración fija, no una exploración de parámetros. No hay resultados de esa ejecución R guardados junto al script que permitan establecer qué partición obtuvieron sus autores. El comentario sobre valores faltantes antes de K-Means no demuestra que el script nunca se haya ejecutado.

El notebook `Legacy/migracion_inicial/03_analisis_extra.ipynb` sí conserva salidas de una ejecución de la migración a Python: DBSCAN produjo un grupo con 2.393 observaciones sin ruido y Silhouette no disponible. Ese registro es evidencia de la migración, no una salida histórica de R.
