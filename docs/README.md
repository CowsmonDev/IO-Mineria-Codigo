# Documentación del proyecto

Pregunta central: **¿cómo cambia el agrupamiento de los mismos estudiantes al aplicar K-Means y DBSCAN sobre la misma entrada académica usada por el jerárquico?**

El output principal es la asignación de cada alumno a un grupo. A partir de ella cambian los tamaños, las características académicas y la separación de los grupos. DBSCAN puede dejar alumnos como ruido. La interpretación busca relacionar esos cambios con los perfiles descritos por el estudio previo.

## Guía de lectura

| Documento | Propósito |
|---|---|
| [Criterios del trabajo](criterios-del-trabajo.md) | Objetivo, alcance, comparación prevista y equivalencia R–Python aceptada. |
| [Informe](referencias/informe.md) | Borrador académico con entrada, métodos, resultados actuales y preguntas que debe responder la comparación. |
| [Flujo por archivos](flujos/flujo-archivos.md) | Recorrido de los datos y salidas realmente implementadas. |
| [Informe final de DBSCAN](resultados/experiencia-dbscan.pdf) | Documento principal: cinco casos, interpretación y decisión de no adoptarlo como segmentación seleccionada. |
| [Fuente editable del informe](resultados/experiencia-dbscan.docx) | Versión Word para actualizar el documento principal. |
| [Anexo técnico de DBSCAN](resultados/anexo-tecnico-dbscan.md) | Protocolos, tablas de exploración, concordancia, sensibilidad, diagnóstico sin `deserto` y casos del código actual. |
| [Verificación R–Python](resultados/verificacion-fechas-r-python.md) | Validación cerrada de alumnos, atributos y agrupamientos en cinco fechas. |

La evaluación de DBSCAN está cerrada bajo el protocolo estudiado. El informe final es la referencia para sus conclusiones; el anexo conserva la evidencia detallada. Las búsquedas históricas no se ejecutan desde `main.py`. El antecedente de K-Means se conserva dentro del [borrador general](referencias/informe.md#anexo-histórico-de-k-means).

## Referencias originales

- [Informe de Clementi y Salias](referencias/IO-Mineria-Informe-Clementi-Salias.pdf): sección 4.3, perfiles de clusters; sección 5, conclusiones y trabajos futuros.
- [Artículo en inglés](<referencias/Analyzing students dropout using penalized logistic regression and hierarchical clustering a case study in systems engineering.docx.pdf>): sección 4.4, perfiles; sección 5, líneas de continuidad.
- [Scripts R](../Legacy/scripts): implementación del procesamiento, LASSO y clustering original.

Los PDF se conservan como fuentes. La documentación distingue lo publicado, lo obtenido con el código actual y los análisis pendientes. La fecha de trabajo es `2026-10-01`. El requisito de equivalencia R–Python está verificado; reproducir la fecha o las cifras publicadas queda fuera de alcance.

Para instalar y ejecutar el proyecto, consultar el [README principal](../README.md).
