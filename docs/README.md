# Documentación del proyecto

Pregunta central: **¿cómo cambia el agrupamiento de los mismos estudiantes al aplicar K-Means y DBSCAN sobre la misma entrada académica usada por el jerárquico?**

El output principal es la asignación de cada alumno a un grupo. A partir de ella cambian los tamaños, las características académicas y la separación de los grupos. DBSCAN puede dejar alumnos como ruido. La interpretación busca relacionar esos cambios con los perfiles descritos por el estudio previo.

## Guía de lectura

| Documento | Propósito |
|---|---|
| [Criterios del trabajo](criterios-del-trabajo.md) | Objetivo, alcance, comparación prevista y equivalencia R–Python aceptada. |
| [Informe](referencias/informe.md) | Borrador académico con entrada, métodos, resultados actuales y preguntas que debe responder la comparación. |
| [Flujo por archivos](flujos/flujo-archivos.md) | Recorrido de los datos y salidas realmente implementadas. |
| [Resultados K-Means](resultados/resultados-kmeans.md) | Ejecución principal y registro histórico de la primera comparación y sus repeticiones. |
| [Resultados DBSCAN](resultados/resultados-dbscan.md) | Configuración inicial, resultado observado y criterios para su exploración posterior. |

- [Verificación de fechas R–Python](resultados/verificacion-fechas-r-python.md): validación cerrada de alumnos, atributos y agrupamientos en cinco fechas.

- [Exploración de DBSCAN](resultados/exploracion-dbscan.md): dieciséis configuraciones, cobertura, perfiles y sensibilidad local.

- [Ampliación de DBSCAN y nube de puntos](resultados/ampliacion-dbscan.md): más grupos, sensibilidad a parámetros y orden, y proyección 2D con PCA.

- [Siete grupos y concordancia de DBSCAN](resultados/concordancia-dbscan.md): búsqueda acotada, ruido, correspondencia con el jerárquico y sensibilidad.

## Referencias originales

- [Informe de Clementi y Salias](referencias/IO-Mineria-Informe-Clementi-Salias.pdf): sección 4.3, perfiles de clusters; sección 5, conclusiones y trabajos futuros.
- [Artículo en inglés](<referencias/Analyzing students dropout using penalized logistic regression and hierarchical clustering a case study in systems engineering.docx.pdf>): sección 4.4, perfiles; sección 5, líneas de continuidad.
- [Scripts R](../Legacy/scripts): implementación del procesamiento, LASSO y clustering original.

Los PDF se conservan como fuentes. La documentación distingue lo publicado, lo obtenido con el código actual y los análisis pendientes. La fecha de trabajo es `2026-10-01`. El requisito de equivalencia R–Python está verificado; reproducir la fecha o las cifras publicadas queda fuera de alcance.

Para instalar y ejecutar el proyecto, consultar el [README principal](../README.md).
