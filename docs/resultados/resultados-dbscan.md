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
