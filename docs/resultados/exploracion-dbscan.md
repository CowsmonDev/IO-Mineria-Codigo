# Exploración explícita de DBSCAN

Realizada el 5 de octubre de 2026. Fecha de análisis: `2026-10-01`. Se conservó la entrada actual: 2.587 alumnos, diez atributos estandarizados con desvío muestral y distancia euclídea. Esta prueba no modifica los parámetros predeterminados ni compara contra R.

## Configuraciones y criterio de exploración

Se inspeccionó la curva de vecinos. Para min_samples 5, 10 y 20, las medianas de distancia al vecino que completa el mínimo son 0,162, 0,281 y 0,386; los percentiles 90 son 1,301, 1,520 y 1,774. Hay una zona densa de distancias pequeñas y una cola de alumnos más aislados; no se asumió un codo único como selección automática.

La primera tanda fue eps={0,6; 0,8; 1,0; 1,5} con min_samples={5; 10; 20}. Como persistía un grupo dominante, se añadieron cuatro radios con min_samples=10: 0,3 y 0,4 para examinar fragmentación, y 0,9 y 1,1 para sensibilidad local. Total: dieciséis configuraciones explícitas.

## Resultados

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

## Patrón observado

- Con eps=1,5 queda un único grupo para los tres mínimos probados.
- Con min_samples=5, radios menores forman grupos pequeños y uno muy grande. Silhouette es negativo con eps=0,6 y 0,8 y apenas positivo con eps=1,0.
- Con min_samples=10 y eps entre 0,8 y 1,1 aparecen tres grupos. El mayor concentra entre 2.109 y 2.183 alumnos; los otros son pequeños. El ruido baja de 409 a 313 alumnos y Silhouette sube de 0,0444 a 0,0778.
- El mayor Silhouette de la exploración es 0,0961 con eps=0,3 y mínimo 10, pero deja 44,3 % de alumnos como ruido y forma 18 grupos. Ese valor corresponde a una cobertura distinta y no justifica elegir la configuración.
- Con mínimo 20 predominan uno o dos grupos y crece el ruido.

Estas pruebas permiten calcular Silhouette para varias configuraciones, pero no muestran una segmentación claramente separada y distribuida entre varios perfiles de tamaño relevante.

## Características de una configuración representativa

Para eps=1,1 y min_samples=10:

| Categoría | Alumnos | Finales aprobados, media | Promocionadas, media | Deserción |
|---|---:|---:|---:|---:|
| Grupo 1 | 2.183 | 1,887 | 0 | 100 % |
| Grupo 2 | 70 | 1,643 | 1 | 100 % |
| Grupo 3 | 21 | 2,333 | 2 | 100 % |
| Ruido | 313 | 9,249 | 1,431 | 76,36 % |

En esta configuración, los grupos pequeños se distinguen especialmente por la cantidad de promociones, mientras el grupo principal incluye alumnos de bajo avance y sin promociones. El ruido contiene trayectorias de mayor avance medio y todos los 74 alumnos marcados como no desertores.

Los 74 no desertores quedaron como ruido en las dieciséis configuraciones, no solo en la representativa. Ruido no significa deserción ni error: refleja que no quedaron integrados en regiones suficientemente densas bajo esos parámetros. Como deserto participa en la matriz, estas proporciones son descriptivas y no validan una predicción.

## Sensibilidad local

Con mínimo 10, se compararon radios vecinos 0,8–0,9, 0,9–1,0 y 1,0–1,1. Entre los alumnos agrupados en ambas configuraciones, ARI=1 en los tres pares (2.178, 2.229 y 2.248 alumnos respectivamente).

Esto indica que sus agrupamientos se conservan en el subconjunto común; cambia qué alumnos pasan del ruido a un grupo. No demuestra estabilidad de toda la población ni frente a otras muestras o parámetros fuera del intervalo probado.

La exploración continuó con [35 configuraciones adicionales, sensibilidad y nube PCA](ampliacion-dbscan.md). Esta nota conserva los resultados de la primera tanda.

## Conclusión y configuración predeterminada

No se selecciona automáticamente una configuración final. eps=1,0 o 1,1 con mínimo 10 son casos útiles para inspeccionar tres grupos y su ruido, pero conservan un grupo dominante y Silhouette bajo. Reducir mucho el radio aumenta fragmentación y exclusión.

El resultado relevante es que, sobre esta entrada, las configuraciones ensayadas tienden a recuperar una región dominante de alumnos marcados como desertores y pequeñas regiones asociadas a promociones, dejando otras trayectorias como ruido. La exploración no garantiza que exista una configuración que forme perfiles amplios y bien separados.

Los valores predeterminados del código permanecen eps=1,5 y min_samples=5. La elección de una configuración para el informe se discutirá a partir de estos resultados, sin exigir siete grupos.

## Evidencia y reproducción

En `output/dbscan/experimentos/dbscan_2026-10-01/` quedan:

- `resumen_configuraciones.csv`, con tamaños, ruido, Silhouette y cobertura de cada prueba.
- `sensibilidad_local.csv`, con la comparación restringida a alumnos agrupados en ambas configuraciones.
- `vecinos_configuraciones.png` y `ruido_silhouette.png`, gráficos de síntesis.
- Una carpeta por configuración con `dbscan/perfiles.csv`, `dbscan/asignaciones.csv` y `dbscan/graficos/`.
- `configuracion.json`, con parámetros, versiones y huella de la matriz; `ejecucion.log` y `ejecutar_pruebas.py`.

Se verificaron identidad y cantidad de asignaciones, suma de tamaños, conteo de grupos y ruido, y la observación sobre los 74 no desertores. Se inspeccionaron los gráficos de síntesis, perfiles y Silhouette. Los archivos de experimentos están excluidos de Git y no se generan por la ejecución habitual de main.

Para repetir las pruebas desde la raíz del proyecto:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 PYTHONPATH=. uv run python output/dbscan/experimentos/dbscan_2026-10-01/ejecutar_pruebas.py
```

Ver [configuración inicial de DBSCAN](resultados-dbscan.md) y [criterios del trabajo](../criterios-del-trabajo.md).
