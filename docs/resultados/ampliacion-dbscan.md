# Ampliación de parámetros y nube de puntos de DBSCAN

Realizada el 5 de octubre de 2026 sobre la misma entrada de la [primera exploración](exploracion-dbscan.md): 2.587 alumnos, diez atributos y fecha de análisis `2026-10-01`. Se comprobó la huella de la matriz para asegurar que la entrada no cambió. Los parámetros predeterminados del código permanecen iguales.

## Pregunta

¿Se pueden obtener más grupos que los tres encontrados alrededor de eps=1,0 y mínimo 10, con una segmentación más útil y menos sensible a pequeñas variaciones?

Tres grupos no son insuficientes por definición. Se examinan cantidad, tamaños, cobertura, características y sensibilidad; aumentar el número no garantiza mejorar los perfiles.

## Configuraciones

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

## Más grupos y características

Con eps=0,5 y mínimo 10 se obtienen siete grupos, de tamaños 1.498, 152, 15, 82, 61, 19 y 11, más 749 alumnos como ruido (28,95 %). Silhouette es −0,0419 y el mayor grupo concentra 81,5 % de los agrupados.

Los grupos pequeños se distinguen fuertemente por valores discretos de los atributos: por ejemplo, los grupos 2, 4, 5 y 6 tienen exactamente 1, 2, 3 y 4 finales desaprobados respectivamente; el grupo 3 tiene una promoción. Esto describe una separación asociada a esos atributos, no demuestra por sí solo perfiles académicos amplios e independientes.

Con eps=0,2 y mínimo 5 se obtienen 53 grupos y Silhouette de 0,3516, pero queda 45,15 % como ruido. Al reducir eps a 0,18 aparecen 59 grupos y Silhouette de 0,4823, con 45,84 % de ruido. Son soluciones mucho más fragmentadas y muchas agrupaciones tienen pocos alumnos; su mayor Silhouette no justifica automáticamente elegirlas.

## Sensibilidad a los parámetros

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

## Sensibilidad al orden de filas

Se probaron cinco permutaciones de la entrada para 0,5/10 y 0,2/5, manteniendo los datos y parámetros. En 0,5/10 las particiones coincidieron completamente y ningún alumno cambió su condición de ruido. En 0,2/5 ARI en comunes fue 0,9981, sin cambios ruido/grupo; se observan pequeñas diferencias de asignación compatibles con puntos de borde.

Reproducibilidad al cambiar el orden no equivale a estabilidad frente a los parámetros o cambios en la muestra. No se realizaron pruebas de remuestreo.

## Nube de puntos en dos dimensiones

Cada alumno ocupa un punto en el espacio original de diez atributos estandarizados. Se ajustó una única PCA de dos componentes sobre toda la matriz para visualizar las soluciones 0,5/10 (siete grupos) y 1,1/10 (tres grupos) con la misma proyección y escalas.

- Componente 1: 45,7919 % de la varianza.
- Componente 2: 22,7740 %.
- Total representado: 68,5660 %.

Los ejes son combinaciones lineales de los atributos, no atributos individuales. Cada punto corresponde a un alumno; color indica el grupo y gris indica ruido. Los puntos coincidentes pueden superponerse. Las etiquetas se calcularon en diez dimensiones, no sobre la proyección. PCA se usa solo para visualizar y no modifica la entrada de DBSCAN.

La proyección pierde aproximadamente 31,4 % de la varianza: grupos distintos pueden verse superpuestos y la distancia dibujada no equivale a la distancia completa usada por DBSCAN. La nube ilustra cambios de asignación y ruido, no reemplaza el análisis de perfiles o sensibilidad.

## Conclusión de esta tanda

Se pueden obtener más grupos, pero las combinaciones examinadas introducen fragmentación, ruido alto o sensibilidad al radio. La solución 0,5/10 es un caso útil para inspeccionar siete grupos y contrastarlo con la solución de tres; no se selecciona como definitiva solo por coincidir con la cantidad del jerárquico.

No se modifican los parámetros predeterminados. La evidencia disponible no permite afirmar que hayamos encontrado varios perfiles de tamaños relevantes, buena cobertura y estabilidad amplia de parámetros sobre esta entrada.

## Archivos y reproducción

En `output/dbscan/experimentos/dbscan_ampliacion_2026-10-01/` se guardaron:

- `resumen.csv`, perfiles y asignaciones por configuración.
- `sensibilidad.csv` y `sensibilidad_orden.csv`.
- `grupos_ruido_dominio.png`, `silhouette.png` y gráficos de casos seleccionados.
- `nube_pca_dbscan.png`, `proyeccion_pca.csv`, `componentes_pca.csv` y `pca.json`.
- `configuracion.json`, `ejecucion.log` y los tres scripts para repetir pruebas y figuras.

Desde la raíz:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 PYTHONPATH=. uv run python output/dbscan/experimentos/dbscan_ampliacion_2026-10-01/explorar.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 PYTHONPATH=. uv run python output/dbscan/experimentos/dbscan_ampliacion_2026-10-01/evaluar_sensibilidad.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 PYTHONPATH=. uv run python output/dbscan/experimentos/dbscan_ampliacion_2026-10-01/graficar_nube.py
```

El gráfico de tres grupos toma las asignaciones de la primera exploración, que deben estar disponibles. Las pruebas y archivos no forman parte de la ejecución habitual de main y están excluidos de Git.

Referencia para la visualización: [PCA en scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html).
