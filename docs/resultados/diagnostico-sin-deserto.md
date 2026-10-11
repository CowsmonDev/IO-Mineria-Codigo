# Diagnóstico auxiliar: retirar `deserto`

Ejecutado el 5 de octubre de 2026, sobre la fecha de análisis `2026-10-01`.

## Alcance

Esta prueba responde únicamente a la duda de si `deserto` explica la concentración de DBSCAN. Por decisión del trabajo, **no forma parte de la comparación principal ni se utiliza para elegir su configuración final**. La comparación principal conserva los diez atributos originales y la misma entrada para los tres métodos.

Se conservaron los 2.587 alumnos, su orden y los valores estandarizados de los otros nueve atributos. Se retiró solo la columna `deserto`, sin filtros ni ajustes de escalado adicionales. El código de producción, sus esquemas y parámetros predeterminados no se modificaron.

Se ejecutaron cinco configuraciones fijas de DBSCAN con y sin esa columna, además del jerárquico Ward con corte a altura 35 y K-Means con k=7 y los parámetros existentes. No se realizó una nueva búsqueda de parámetros. `deserto` se conservó en los datos originales para describir los grupos, pero no intervino en la matriz de nueve atributos.

## DBSCAN: resultados idénticos en las cinco configuraciones

| eps / min_samples | Grupos, con y sin `deserto` | Ruido, con y sin `deserto` | Grupo mayor entre agrupados, con y sin `deserto` |
|---|---:|---:|---:|
| 1,5 / 5 | 1 | 194 (7,50 %) | 100,00 % |
| 1,1 / 10 | 3 | 313 (12,10 %) | 96,00 % |
| 0,5 / 10 | 7 | 749 (28,95 %) | 81,50 % |
| 0,5 / 6 | 14 | 632 (24,43 %) | 77,29 % |
| 1,175 / 4 | 7 | 244 (9,43 %) | 94,54 % |

Se verificó igualdad exacta de etiquetas por alumno, incluidos los alumnos marcados como ruido. ARI=1 en las cinco comparaciones. Los 74 alumnos con `deserto=0` siguieron como ruido en todos estos casos. Silhouette también coincide dentro de la precisión numérica.

Dentro de estas cinco configuraciones, la concentración persiste al retirar la columna: no puede atribuirse solamente a su inclusión. Esto no demuestra que `deserto` nunca afecte a DBSCAN con otros parámetros.

## Los otros métodos sí cambian

| Método | Con `deserto` | Sin `deserto` | ARI entre ambas asignaciones |
|---|---|---|---:|
| Jerárquico, Ward h=35 | 7 grupos; tamaños 903, 636, 355, 332, 236, 74, 51 | 6 grupos; tamaños 903, 636, 508, 350, 128, 62 | 0,936084 |
| K-Means, k=7 | 7 grupos; tamaños 1101, 506, 405, 326, 95, 81, 73 | 7 grupos; tamaños 1150, 507, 385, 332, 107, 59, 47 | 0,907459 |

El jerárquico se calculó directamente con SciPy usando el mismo enlace y altura, para observar la cantidad resultante sin la exigencia de siete grupos del módulo de producción. La ejecución de control con diez atributos coincide en asignaciones con la referencia actual. No se ajustó el corte para recuperar siete grupos.

La retirada de una variable sí puede modificar la estructura y las asignaciones. Su efecto depende del método y de los parámetros.

## Archivos locales

La prueba está en `output/dbscan/experimentos/diagnostico_sin_deserto_2026-10-01/`, excluida de Git junto con el resto de `output/`:

- `diagnostico.py`, `configuracion.json` y `ejecucion.log`: protocolo, versiones y huellas de ambas matrices.
- `resumen.csv`, `cambios.csv` y tablas cruzadas entre variantes.
- `con_deserto/` y `sin_deserto/`: asignaciones por alumno y perfiles de cada método/configuración.
- `graficar.py` y `graficos/comparacion_con_sin_deserto.png`.

Reproducción local desde la raíz:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 PYTHONPATH=. uv run python output/dbscan/experimentos/diagnostico_sin_deserto_2026-10-01/diagnostico.py
uv run python output/dbscan/experimentos/diagnostico_sin_deserto_2026-10-01/graficar.py
```

La entrada principal continúa siendo la de diez atributos. Este diagnóstico queda separado de las conclusiones comparativas del proyecto.
