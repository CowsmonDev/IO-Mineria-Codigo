# Objetivo y alcance de la comparación

Actualizado el 5 de octubre de 2026.

## Pregunta y objetivo

**¿Cómo cambia la agrupación de los mismos estudiantes al aplicar K-Means y DBSCAN sobre los mismos atributos utilizados por el clustering jerárquico?**

El objetivo es comparar la cantidad de grupos, sus integrantes y sus características académicas, e interpretar si los perfiles del estudio de referencia se conservan, se dividen, se fusionan o quedan parcialmente como ruido.

La comparación se basa en una entrada común reproducible. El jerárquico es una referencia de agrupamiento, no una clasificación verdadera que los métodos alternativos deban reproducir. Obtener un Silhouette mayor aporta información sobre separación, pero no responde por sí solo a la pregunta del trabajo.

## Relación con trabajos futuros

El informe de Clementi y Salias propone incorporar indicadores socioeconómicos y contextuales y luego aplicar K-Means y DBSCAN para contrastar la estabilidad de los perfiles hallados. El artículo en inglés también incluye los métodos alternativos como línea de validación y continuidad.

Esta extensión desarrolla la comparación sobre los datos académicos existentes. La incorporación de nuevas fuentes, los modelos predictivos supervisados y una herramienta institucional de alertas quedan fuera del alcance actual.

## Qué se conserva y qué cambia

Se mantienen, para una misma ejecución, la fuente de datos, población, filtros, atributos, fecha de análisis, transformaciones, estandarización y orden de alumnos. Los tres algoritmos reciben la misma matriz. Las etiquetas del jerárquico no se incluyen como atributos de los demás métodos.

Cada método produce su propio agrupamiento:

| Método | Decisión que define los grupos | Configuración actual |
|---|---|---|
| Jerárquico | Enlace y corte del árbol | Euclídea, Ward, h=35; se comprueba que produzca siete grupos. |
| K-Means | Número de centros e inicialización | k=7, k-means++, 25 inicializaciones, semilla 123. |
| DBSCAN | Radio y densidad mínima | eps=1,5; min_samples=5, incluido el propio alumno. |

K-Means tiene siete grupos por decisión del protocolo actual, pero puede asignar integrantes distintos. DBSCAN determina su cantidad de grupos y puede dejar alumnos como ruido. No se le exige producir siete ni coincidir con los grupos jerárquicos.

La entrada de trabajo actual, con fecha `2026-10-01`, contiene 2.587 alumnos y diez atributos. Las definiciones están en [informe.md](referencias/informe.md#3-entrada-común). El indicador de actividad de «último año» conserva el año 2023 del procesamiento original.

## Qué output se compara

1. **Asignaciones:** qué alumnos quedan juntos y cuáles cambian de grupo.
2. **Estructura:** cantidad, tamaños y proporciones de los grupos; cobertura y ruido de DBSCAN.
3. **Características:** medias y distribuciones en unidades originales para describir cada perfil.
4. **Separación:** Silhouette, cuando se puede calcular, con la población evaluada explícita.
5. **Sensibilidad:** cambios entre inicializaciones de K-Means y configuraciones cercanas de DBSCAN.

Las correspondencias se estudiarán con tablas cruzadas de integrantes. Las etiquetas numéricas no implican equivalencia entre métodos. ARI puede complementar estas tablas como medida de concordancia; no expresa exactitud ni porcentaje de aciertos.

La concordancia entre métodos y la sensibilidad dentro de un método son preguntas distintas. Ambas pueden aportar evidencia sobre la robustez de los perfiles.

Si Silhouette de DBSCAN excluye ruido, se informa cuántos alumnos quedan incluidos. Para una comparación sobre la misma población puede calcularse también Silhouette de los otros métodos sobre ese subconjunto, manteniendo sus asignaciones y comprobando que la partición permita calcularlo.

## Equivalencia R–Python y referencia de trabajo

Decisión registrada el 5 de octubre de 2026: el requisito es que R y Python produzcan resultados equivalentes al recibir los mismos datos y la misma fecha de análisis. Reproducir la fecha, las cifras o las figuras publicadas no es un requisito del proyecto.

La [verificación R–Python](resultados/verificacion-fechas-r-python.md) comprobó cinco fechas. En todas, coinciden los 2.587 alumnos, los diez atributos, las matrices dentro de la precisión numérica, las asignaciones por alumno (ARI=1) y Silhouette. La comparación se alineó por `id_alumno`; los números de las etiquetas pueden diferir sin alterar los grupos.

Se acepta el jerárquico de Python como referencia equivalente al de R para las entradas verificadas. La entrada de trabajo sigue fijada en `2026-10-01` y será común a los tres métodos. Los PDF se conservan como antecedentes del problema y de la propuesta de extensión.

La comprobación de la migración queda cerrada para este alcance. Se abandona la búsqueda de una fecha o ejecución que reproduzca íntegramente el informe y no se programan nuevas comparaciones R–Python.

## Papel de LASSO y deserción

LASSO se conserva como antecedente independiente. En el código original, sus coeficientes no seleccionan ni ponderan las variables del clustering. Este proyecto no desarrolla una comparación de modelos de regresión.

`deserto` integra la entrada, como en el original. Su proporción por grupo describe la composición; no es una validación independiente de capacidad predictiva ni demuestra causas del abandono.

## Estado y próximos análisis

Los tres métodos, sus resúmenes y gráficos individuales están implementados. Se realizaron exploraciones locales de DBSCAN, incluida una [búsqueda de siete grupos con poco ruido y concordancia con el jerárquico](resultados/concordancia-dbscan.md). Se registraron tablas cruzadas y sensibilidad de los candidatos; no se eligió una nueva configuración final. Las repeticiones históricas de K-Means se conservan como antecedentes, sin ejecutarse automáticamente.

La validación de la migración está cerrada y no bloquea el objetivo del proyecto. La comparación completa de perfiles entre los tres métodos sigue pendiente. Los experimentos de DBSCAN son análisis locales y no se ejecutan automáticamente desde `main.py`.

## Fuentes

- [Informe original](referencias/IO-Mineria-Informe-Clementi-Salias.pdf), secciones 3.2.1, 4.3 y 5.
- [Artículo en inglés](<referencias/Analyzing students dropout using penalized logistic regression and hierarchical clustering a case study in systems engineering.docx.pdf>), secciones 3, 4.4 y 5.
- [Procesamiento R](../Legacy/scripts/script_manipulacion_datos_2025.R) y [análisis jerárquico R](../Legacy/scripts/script_analisis_preliminar_2025.R).
