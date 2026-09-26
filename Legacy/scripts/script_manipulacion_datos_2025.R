# Libreria necesaria para filtrar, agrupar y resumir datos.
library(dplyr)
# Libreria necesaria para trabajar con fechas y horas
library(lubridate)
# Libreria necesaria para crear datos ordenados
library(tidyr)

# Generación de dataframes a partir de los datos del SIU Guarani
# dataframes:
# alumnos: contiene los datos de los alumnos anotados en la Facultad de Ciencias Exactas
# cursadas: contiene los datos de las cursadas de los alumnos de la Facultad de Cs. Exactas
# finales: contiene los datos de los exámenes finales rendidos por los alumnos de la Facultad de Cs. Exactas
# planes: contiene los datos de los planes de estudio de las carreras de la Facultad de Cs. Exactas

alumnos <- read.csv("data/001_alumnos.csv", header = TRUE, sep = "|")

cursadas <- read.csv("data/002_regularidades.csv", sep = "|", stringsAsFactors = FALSE)

finales <- read.csv("data/003_historia_academica.csv", sep = "|", stringsAsFactors = FALSE)

planes <- read.csv("data/000_materias_planes.csv", sep = "|", stringsAsFactors = FALSE)

# Filtrado del dataframe de alumnos con alumnos que ingresaron posteriormente al
# año 2011 y antes del 2024 para tener certeza de que los datos estén más completos
# la carrera elegida es ingeniería de sistemas(206) dónde queremos focalizar el analisis
alumnos <- alumnos %>% filter(fecha_inscripcion > "2011-01-01" & fecha_inscripcion < "2023-12-31" & carrera == 206 & !calidad == 'Egreso')

# Eliminamos a un alumno de intercambio que no nos sirve para el análisis
alumnos_inscriptos <- alumnos %>% filter(!id_alumno == 109662)

# Quitamos las PPS, las optativas y el proyecto final de los planes de estudio
planes <- planes %>% filter(carrera == 206 & obligatoria == "S" & !materia %in% c("0205", "6523", "PPS"))

cursadas <- cursadas %>% filter(carrera == 206)

cursadas <- inner_join(cursadas, planes, by = c("plan", "carrera", "materia", "nombre_materia"))

finales <- finales %>% filter(carrera == 206 & !materia %in% c("PPS", "P0001", "P0002", "0205"))

finales <- inner_join(finales, planes, by = c("plan", "carrera", "materia", "nombre_materia"))

# Eliminacion de filas repetidas
alumnos_inscriptos <- distinct(alumnos_inscriptos)
alumnos_inscriptos <- alumnos_inscriptos %>%
  group_by(id_alumno) %>%
  slice_head(n = 1) %>%  # o slice(1)
  ungroup()


# ALUMNOS QUE DESAPROBARON ALGUNA MATERIA IMPORTANTE DE LA CARRERA

alumnos_desaprob_mat_IS <- inner_join(alumnos_inscriptos, cursadas, by = c("id_alumno", "plan", "carrera")) %>%
  filter(
    nombre_materia %in% c(
      "Introducción a la Programación I", 
      "Introducción a la Programación II", 
      "Análisis y Diseño de Algoritmos I", 
      "Análisis y Diseño de Algoritmos II", 
      "Programación Orientada a Objetos"
    ) & 
      resultado %in% c("R", "U")
  ) %>%
  distinct(id_alumno, carrera, plan, .keep_all = TRUE)

# Filtrado y agrupamiento del data frame planes (000_materias_planes.csv)
# Selecciona solo las filas donde la materia es obligatoria (la col obligatoria tiene valor "S")
# agrupa los datos por "carrera" y "plan"
# calcula el nro de materias OBLIGATORIAS por "carrera" y "plan"
# Limpia el campo "plan" eliminando los finales como "2020.0" -> "2020" usando una expresion regular

planes_materias <- planes %>%
  filter(obligatoria == "S") %>%
  group_by(carrera, plan) %>%
  summarize(cant_materias = n()) %>%
  mutate(plan = sub("[.]0$", "", as.character(plan)))

# Conversion del resultado en un vector con nombres
# Convierte el data frame "planes_materias" en un vector con nombres, donde:
# Los valores son las cantidades de materias (cant_materias).
# Los nombres son combinaciones de carrera y plan, separadas por coma, como "Sistemas, 2020".

planes_materias <- setNames(planes_materias$cant_materias,
                            planes_materias$plan)

# Limpieza del campo "plan" en cursadas:
# Esta línea modifica la columna plan del data frame cursadas
# Usa sub() para reemplazar un patrón: si el contenido termina en ".0" (por ejemplo "2020.0"), lo reemplaza con una cadena vacía, es decir, lo elimina.
# Resultado: "2020.0" → "2020".
# Esto estandariza los valores del campo plan.
# Lo mismo para finales

cursadas$plan <- sub("[.]0$", "", cursadas$plan)
finales$plan <- sub("[.]0$", "", finales$plan)
cursadas$nota <- as.numeric(gsub(",", ".", cursadas$nota))
finales$nota <- as.numeric(gsub(",", ".", finales$nota))

# Manipulación de datos uniendo los dataframes de alumnos y notas cursadas.
# Las variables que nos interesa obtener son: 
# porcentaje de avance de cursadas
# promedio de las notas obtenidas en el ultimo año
# cantidad de materia que cursó en el ultimo año
# materias aprobadas en total
# materias promocionadas en total
# materias recursadas

# Agrupación y resumen de cursadas: Agrupa las cursadas por estudiante (id_alumno), carrera y plan. Luego calcula:
alumnos_con_cursadas <- cursadas %>%
  group_by(id_alumno, carrera, plan) %>%
  summarise(
    # Cálculos por estudiantes
    # Cuenta cuántas materias fueron aprobadas
    cursadas_aprobadas = length(materia[resultado == "A"]),
    # Cuenta solo las aprobadas con final ("A").
    cursadas_regulares = length(materia[resultado == "A" & cond_regularidad == "Regular"]),
    # Cuenta cuántas materias fueron promocionadas
    cursadas_promocionadas = length(materia[resultado == "A" & cond_regularidad == "Promocionó"]),
    # Cuenta las cursadas desaprobadas: "U" (ausente) o "R" (reprobado).
    cursadas_desaprobadas = length(materia[resultado == "U" | resultado == "R"]),
    # Promedio de notas de las materias regularizadas durante el año 2023.
    notas_cursadas_ult_anio = mean(nota[(fecha_regularidad <= "2023-12-31" & fecha_regularidad >="2023-01-01")], na.rm = TRUE),
    # Cantidad de materias únicas en las que el alumno se anotó (y obtuvo regularidad) en el año 2023.
    materias_anotado_ult_anio = length(unique(materia[(fecha_regularidad <= "2023-12-31" & fecha_regularidad >= "2023-01-01")]))
  ) %>%
  # Calcula el porcentaje de materias aprobadas respecto al total
  mutate(porc_cursadas = cursadas_aprobadas / planes_materias[as.character(plan)]) %>%
  # Une los datos resumidos con el data frame alumnos, conservando todos los estudiantes (incluso si no tienen cursadas registradas). Esto se hace con un right join, donde la tabla "maestra" es alumnos.
  right_join(alumnos_inscriptos[, c("id_alumno","carrera", "plan", "fecha_inscripcion", "localidad_nacimiento", "calidad")], by = c("id_alumno", "carrera", "plan"))%>%
  
  # Reemplaza con 0 los valores faltantes (NA) en los campos clave. Esto es útil para alumnos sin cursadas registradas.
  replace_na(list(
    cursadas_aprobadas = 0,
    cursadas_regulares = 0,
    cursadas_promocionadas = 0,
    cursadas_desaprobadas = 0,
    materias_anotado_ult_anio = 0,
    notas_cursadas_ult_anio = 0,
    porc_cursadas = 0
  ))

# Manipulacion de los datos uniendo los dataframes de alumnos y finales para
# obtener la cantidad de finales rendidos, aprobados, desaprobados y rendidos en el último año
# Agrupa los registros de finales por estudiante (id_alumno), carrera y plan.
alumnos_con_finales <- finales %>%
  group_by(id_alumno, carrera, plan) %>%
  # Dentro del summarise() se calculan varios indicadores:
  # finales_aprobados -> Cuenta la cantidad de finales aprobados ("A").
  # finales_desaprobados -> Cuenta la cantidad de finales desaprobados ("R").
  # nota_finales_ult_anio -> Calcula el promedio de notas de finales posteriores al 1 de enero de 2023. na.rm = TRUE omite valores faltantes (NA) en el cálculo.
  # dias_dsd_ultimo_final -> Calcula la cantidad de días desde el último final rendido hasta la fecha actual (Sys.Date()).
  # Marca si la forma de aprobación fue equivalencia
  mutate(cambio_plan = forma_aprobacion == "Equivalencia") %>%
  summarise(
    finales_aprobados = length(materia[resultado == "A"]),
    finales_desaprobados = length(materia[resultado == "R"]),
    nota_finales_ult_anio = mean(nota[fecha > "2023-01-01"], na.rm = TRUE),
    dias_dsd_ultimo_final = Sys.Date() - as.Date(max(fecha, na.rm = TRUE)),
    # cambio_plan se usa para saber si el alumno cambio de plan,
    # y asi contar los finales aprobados como equivalencia también como cursadas aprobadas
    cambio_plan = any(cambio_plan)  # TRUE si hubo al menos una equivalencia
  ) %>%
  # Unión con el data frame alumnos -> Hace una unión por derecha (right join) para mantener todos los estudiantes, incluso si no tienen finales registrados.
  right_join(alumnos_inscriptos[, c("id_alumno", "carrera", "plan", "fecha_inscripcion")], by = c("id_alumno", "carrera", "plan")) %>%
  # Reemplazo de valores faltantes. Completa con ceros los campos faltantes (NA), útil para estudiantes sin finales registrados.
  mutate(
    dias_dsd_ultimo_final = coalesce(dias_dsd_ultimo_final, Sys.Date() - as.Date(fecha_inscripcion)),
    cambio_plan = coalesce(cambio_plan, FALSE)  # si no hay finales registrados, asumimos FALSE
  ) %>%
  replace_na(list(
    finales_aprobados = 0,
    finales_desaprobados = 0,
    nota_finales_ult_anio = 0
  )) %>%
  select(-fecha_inscripcion)

# unión de los dataframes para obtener un dataframe central

# Calcular tiempo desde el ingreso. 
# Agrega una nueva columna tiempo_desde_ingreso, que indica cuántos días han pasado desde que el estudiante ingresó.
alumnos_cursadas_finales <- alumnos %>%
  mutate(tiempo_desde_ingreso = Sys.Date() - as.Date(fecha_inscripcion)) %>%
  #  Selección de columnas clave: Se conservan solo los identificadores del alumno y la nueva columna tiempo_desde_ingreso.
  select(id_alumno, carrera, plan, tiempo_desde_ingreso) %>%
  # Uniones internas (inner joins)
  # Se unen los tres data frames por carrera y plan.
  # Como son inner_join, solo se conservarán los estudiantes que están presentes en los tres data frames (es decir, los que tienen cursadas y finales registrados, además de estar en alumnos).
  inner_join(alumnos_con_cursadas, by = c("id_alumno", "carrera", "plan")) %>%
  inner_join(alumnos_con_finales, by = c("id_alumno", "carrera", "plan")) %>%
  # total_materias_finalizadas: suma de finales aprobados y materias promocionadas (que no necesitan final).
  # porc_finales: porcentaje del plan completo que representa esa suma, dividiendo por el total de materias (materias_sistemas, que vale 44) + 1.
  # Posiblemente se suma 1 para ajustar por alguna materia adicional no contabilizada o por un error conocido del dataset.
  # relacion_finales_cursadas: mide qué proporción de las materias cursadas fueron finalizadas (ya sea con final o promoción).
  mutate(
    cursadas_aprobadas = ifelse(cambio_plan == TRUE, finales_aprobados, cursadas_aprobadas),
    cursadas_regulares = ifelse(cambio_plan == TRUE, cursadas_aprobadas, cursadas_regulares),
    cursadas_desaprobadas = ifelse(cambio_plan == TRUE, finales_desaprobados, cursadas_desaprobadas),
    total_materias_finalizadas = finales_aprobados,
    porc_finales = total_materias_finalizadas / (planes_materias[as.character(plan)]),
    porc_cursadas = ifelse(cambio_plan == TRUE, porc_finales, porc_cursadas),
    relacion_finales_cursadas = ifelse(cursadas_aprobadas == 0, NA, total_materias_finalizadas / cursadas_aprobadas)
  )

# Para eliminar filas repetidas de alumnos_cursadas_finales. Tal vez convenga hacerlo directamente sobre alumnos
alumnos_cursadas_finales <- distinct(alumnos_cursadas_finales)
alumnos_cursadas_finales <- alumnos_cursadas_finales %>%
  group_by(id_alumno) %>%
  slice_head(n = 1) %>%  # o slice(1)
  ungroup()

# filtro para obtener un dataframe con aquellos que tengan menos del 50 % de la carrera avanzada y donde se marca la deserción
alumnos_s_avanzados <- alumnos_cursadas_finales %>%
  # Filtrar alumnos con avance ≤ 50%: Conserva solo los estudiantes que han finalizado como máximo el 50% del plan (entre finales aprobados y materias promocionadas).
  filter(porc_finales <= 0.5) %>%
  # Detección de deserción
  # Se crea una nueva columna lógica llamada deserto que vale TRUE si se cumplen ambas condiciones:
  # 1) Pasaron más de 2 años (730 días) desde que rindió su último final.
  # 2) El estudiante no se anotó a ninguna materia en el último año (año 2023, según los datos usados antes).
  mutate(deserto = (dias_dsd_ultimo_final > days(x = 730) & materias_anotado_ult_anio == 0) | calidad == 'Abandono')

# Lo mismo que arriba, pero para los alumnos que desaprobaron alguna materia de las importantes
alumnos_desaprob_mat_IS <- inner_join(alumnos_desaprob_mat_IS, alumnos_cursadas_finales, by = c("id_alumno", "plan", "carrera", "fecha_inscripcion"))

alumnos_s_avanzados_desaprob_mat_IS <- alumnos_desaprob_mat_IS %>%
  select(-fecha_inscripcion) %>%
  filter(porc_finales <= 0.5) %>%
  mutate(deserto = dias_dsd_ultimo_final > days(x = 730) & materias_anotado_ult_anio == 0 | calidad.x == 'Abandono')

# Separación de alumnos desertores
alumnos_desertores <- alumnos_s_avanzados %>% filter(deserto == TRUE)