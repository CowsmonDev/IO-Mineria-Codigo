# Verificación de fechas: jerárquico en R y Python

Comprobación realizada el 5 de octubre de 2026 sobre los CSV locales. El propósito es verificar la equivalencia del jerárquico en R y Python sobre la misma entrada. Esta comprobación está cerrada para el alcance acordado.

## Procedimiento

Se ejecutó el procesamiento original de R fijando `Sys.Date()` para cada fecha. Del script de análisis se evaluaron la selección numérica, estandarización, distancias euclídeas, Ward, corte h=35 y resumen. No se ejecutaron LASSO ni los gráficos, que no determinan el agrupamiento.

Python utilizó `preparar_entrada(fecha_analisis=...)` y el módulo jerárquico actual cuando el corte produjo siete grupos. Para enero de 2023 se aplicó el mismo enlace y corte directamente con SciPy, pues el módulo actual rechaza cantidades distintas de siete.

Las tablas y matrices se alinearon por `id_alumno`, comparando atributos, asignaciones mediante ARI y Silhouette. ARI=1 indica igualdad de agrupamiento aunque cambien los números de etiquetas.

## Resultados

| Fecha de cálculo | Alumnos | Grupos con h=35 | Silhouette R | Silhouette Python | ARI R–Python |
|---|---:|---:|---:|---:|---:|
| 2023-01-01 | 2.587 | 6 | 0,432666 | 0,432666 | 1 |
| 2023-06-30 | 2.587 | 7 | 0,418796 | 0,418796 | 1 |
| 2023-12-31 | 2.587 | 7 | 0,431358 | 0,431358 | 1 |
| 2025-08-26 | 2.587 | 7 | 0,407122 | 0,407122 | 1 |
| 2026-10-01 | 2.587 | 7 | 0,295444 | 0,295444 | 1 |

En las cinco fechas, la diferencia absoluta máxima entre matrices estandarizadas alineadas fue inferior a 4e-14 y entre atributos originales inferior a 5e-16. La diferencia de Silhouette entre implementaciones fue inferior a 1e-10. La migración reproduce el mismo agrupamiento para cada entrada probada.

## Decisión de alcance

Registrada el 5 de octubre de 2026: importa que ambas implementaciones coincidan entre sí con los mismos datos y fecha. Ese requisito se cumple en las cinco entradas probadas.

Se acepta el jerárquico Python como referencia para el proyecto y se conserva `2026-10-01` como fecha de trabajo común a los tres métodos. Reproducir cifras, figuras o la fecha exacta del informe no es un requisito. Se cierra la investigación de esas diferencias y no se realizarán nuevas comparaciones R–Python sin una nueva solicitud.

La equivalencia está comprobada para las entradas ensayadas; no se presenta como una prueba exhaustiva de todas las fechas o datos posibles. El caso de enero de 2023 también documenta que el corte puede producir seis grupos, mientras el módulo actual exige siete.

## Evidencia y reproducción

Los CSV por fecha, los scripts de verificación y la sesión R quedan en `output/verificacion_fechas/`, excluido de Git. El resumen numérico es `comparacion_r_python.csv`. Se utilizó R en el contenedor `r-base:4.5.1`, con dplyr, tidyr, lubridate y cluster. El contenedor temporal fue eliminado al terminar.

El script Python puede ejecutarse desde la raíz, con las salidas R ya disponibles:

```bash
PYTHONPATH=. uv run python output/verificacion_fechas/comparar_python.py
```

Fuentes: [informe original](../referencias/IO-Mineria-Informe-Clementi-Salias.pdf), secciones 4.3 y 3.2.1, y [procesamiento original en R](../../Legacy/scripts/script_manipulacion_datos_2025.R).
