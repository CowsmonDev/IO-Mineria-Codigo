# DBSCAN: siete grupos, ruido y concordancia con el jerárquico

Fecha de ejecución: 5 de octubre de 2026. Fecha de análisis: `2026-10-01`.

## Pregunta y protocolo

Se exploró si DBSCAN podía producir **siete grupos con hasta 15 % de ruido y una estructura cercana al jerárquico**, sin cambiar los alumnos, atributos ni estandarización. Es una búsqueda de concordancia orientada por la referencia; no es una validación independiente de los siete perfiles ni demuestra que el jerárquico sea una clasificación verdadera.

La entrada contiene 2.587 alumnos y diez atributos. Su SHA-256, sobre los bytes de la matriz NumPy de valores estandarizados, es `39ba3042df7aba74b04409a693c56f36f05f7008c18efc45ffd92c2651dd48c7`.

La búsqueda principal fue una grilla fija de **470 configuraciones**:

- `eps`: de 0,350 a 1,500 inclusive, con paso 0,025 (47 valores).
- `min_samples`: 2, 3, 4, 5, 6, 8, 10, 12, 15 y 20.
- Distancia euclídea sobre la misma matriz estandarizada en diez dimensiones.
- Referencia jerárquica: Ward y corte a altura 35, siete grupos.

Para cada configuración se registraron grupos, ruido, cobertura, tamaños y ARI frente al jerárquico **solo sobre alumnos no marcados como ruido por DBSCAN**. Las etiquetas jerárquicas se conservaron en ese subconjunto; no se volvió a ajustar el árbol. ARI expresa concordancia entre particiones, no porcentaje de aciertos. Valores próximos a cero indican poca concordancia ajustada por azar.

Se encontraron 17 configuraciones con siete grupos; ocho cumplen el límite de ruido. Entre estas ocho se ordenaron los candidatos por ARI descendente. También se inspeccionaron la configuración con menor ruido, la de mayor ARI con siete grupos y la alternativa anterior `0,5/10`. Silhouette se calculó únicamente para esas cinco configuraciones, excluyendo ruido.

## Resultados

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

## Qué se fusiona y qué queda fuera

En `eps=1,175; min_samples=4`, el grupo DBSCAN de 2.215 alumnos mezcla:

- 331 de los 332 alumnos del grupo jerárquico 2.
- 340 de los 355 del grupo jerárquico 5.
- Los 903 del grupo jerárquico 6.
- 579 de los 636 del grupo jerárquico 7.
- 62 del grupo jerárquico 3.

Todos los alumnos del grupo jerárquico 1 (51) y del grupo 4 (74) quedan como ruido. Los 74 alumnos con `deserto=0` también quedan como ruido en este candidato. Esto limita qué perfiles se comparan mediante el ARI sin ruido. En `1,5/3`, tres de esos 74 alumnos sí quedan agrupados: el comportamiento no es idéntico para todas las configuraciones.

La tabla cruzada incluye ruido para hacer visibles esas exclusiones. Tener siete etiquetas no implica conservar siete perfiles semejantes a los jerárquicos.

## Sensibilidad local

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

## Decisión y alcance

No se selecciona una nueva configuración predeterminada de DBSCAN. La búsqueda no encontró una alternativa convincente que reúna siete grupos, poco ruido, menor concentración y cercanía al jerárquico. La conclusión se limita a esta entrada, distancia y grilla; no demuestra que cualquier configuración posible vaya a fallar.

Se recomienda conservar este resultado como evidencia de que los métodos pueden describir estructuras diferentes. Para una partición completa en siete grupos, K-Means permite fijar esa cantidad y comparar sus integrantes con el jerárquico. DBSCAN debe interpretarse por sus regiones densas y exclusiones, aunque no conserve siete perfiles. Revisar atributos, escalado o distancia sería otro experimento y cambiaría el protocolo actual; no se realizó en esta prueba.

## Archivos y reproducción local

Todos los experimentos de DBSCAN están agrupados en `output/dbscan/experimentos/`. Esta prueba está en `dbscan_concordancia_2026-10-01/` y contiene:

- `explorar.py`, `configuracion.json`, `ejecucion.log` y `resumen.csv`: protocolo y grilla completa.
- `siete_grupos.csv`, `seleccion.csv` y `sensibilidad.csv`: candidatos y vecinos.
- Una carpeta por candidato con asignaciones alineadas por `id_alumno`, perfiles, tabla cruzada y `graficos/` con tamaños y correspondencias.
- `graficar.py`: generación de esas figuras a partir de los CSV.

Desde la raíz del proyecto:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 PYTHONPATH=. uv run python output/dbscan/experimentos/dbscan_concordancia_2026-10-01/explorar.py
uv run python output/dbscan/experimentos/dbscan_concordancia_2026-10-01/graficar.py
```

Los scripts y resultados de `output/` son artefactos locales excluidos de Git. Este documento conserva el protocolo, resultados y decisión en el repositorio. `main.py` no ejecuta estas búsquedas automáticamente.
