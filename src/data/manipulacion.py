"""Prepara los datos académicos y devuelve los datos para el análisis preliminar."""

import os
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    os.chdir(Path(__file__).resolve().parents[2])

    # Importaciones y lectura de datos

    # Generación de dataframes a partir de los datos del SIU Guarani
    # dataframes:
    # alumnos: contiene los datos de los alumnos anotados en la Facultad de Ciencias Exactas
    # cursadas: contiene los datos de las cursadas de los alumnos de la Facultad de Cs. Exactas
    # finales: contiene los datos de los exámenes finales rendidos por los alumnos de la Facultad de Cs. Exactas
    # planes: contiene los datos de los planes de estudio de las carreras de la Facultad de Cs. Exactas

    alumnos = pd.read_csv("data/001_alumnos.csv", header=0, sep="|")

    cursadas = pd.read_csv(
        "data/002_regularidades.csv", sep="|", dtype={"materia": str}
    )

    finales = pd.read_csv(
        "data/003_historia_academica.csv", sep="|", dtype={"materia": str}
    )

    planes = pd.read_csv(
        "data/000_materias_planes.csv", sep="|", dtype={"materia": str}
    )

    # Selección de estudiantes y materias

    # Filtrado del dataframe de alumnos con alumnos que ingresaron posteriormente al
    # año 2011 y antes del 2024 para tener certeza de que los datos estén más completos
    # la carrera elegida es ingeniería de sistemas(206) dónde queremos focalizar el analisis
    alumnos = alumnos[
        (alumnos["fecha_inscripcion"] > "2011-01-01")
        & (alumnos["fecha_inscripcion"] < "2023-12-31")
        & (alumnos["carrera"] == 206)
        & (alumnos["calidad"] != "Egreso")
    ].copy()

    # Eliminamos a un alumno de intercambio que no nos sirve para el análisis
    alumnos_inscriptos = alumnos[alumnos["id_alumno"] != 109662].copy()

    # Quitamos las PPS, las optativas y el proyecto final de los planes de estudio
    planes = planes[
        (planes["carrera"] == 206)
        & (planes["obligatoria"] == "S")
        & (~planes["materia"].isin(["0205", "6523", "PPS"]))
    ].copy()

    cursadas = cursadas[cursadas["carrera"] == 206].copy()

    cursadas = cursadas.merge(
        planes,
        how="inner",
        on=["plan", "carrera", "materia", "nombre_materia"],
        suffixes=(".x", ".y"),
    )

    finales = finales[
        (finales["carrera"] == 206)
        & (~finales["materia"].isin(["PPS", "P0001", "P0002", "0205"]))
    ].copy()

    finales = finales.merge(
        planes,
        how="inner",
        on=["plan", "carrera", "materia", "nombre_materia"],
        suffixes=(".x", ".y"),
    )

    # Eliminacion de filas repetidas
    alumnos_inscriptos = alumnos_inscriptos.drop_duplicates().copy()
    alumnos_inscriptos = alumnos_inscriptos.drop_duplicates(
        subset=["id_alumno"], keep="first"
    ).copy()

    # Estudiantes que desaprobaron materias importantes

    # ALUMNOS QUE DESAPROBARON ALGUNA MATERIA IMPORTANTE DE LA CARRERA

    alumnos_desaprob_mat_IS = alumnos_inscriptos.merge(
        cursadas,
        how="inner",
        on=["id_alumno", "plan", "carrera"],
        suffixes=(".x", ".y"),
    )
    alumnos_desaprob_mat_IS = alumnos_desaprob_mat_IS[
        alumnos_desaprob_mat_IS["nombre_materia"].isin(
            [
                "Introducción a la Programación I",
                "Introducción a la Programación II",
                "Análisis y Diseño de Algoritmos I",
                "Análisis y Diseño de Algoritmos II",
                "Programación Orientada a Objetos",
            ]
        )
        & alumnos_desaprob_mat_IS["resultado"].isin(["R", "U"])
    ].copy()
    alumnos_desaprob_mat_IS = alumnos_desaprob_mat_IS.drop_duplicates(
        subset=["id_alumno", "carrera", "plan"], keep="first"
    ).copy()

    # Planes y normalización de campos

    # Filtrado y agrupamiento del data frame planes (000_materias_planes.csv)
    # Selecciona solo las filas donde la materia es obligatoria (la col obligatoria tiene valor "S")
    # agrupa los datos por "carrera" y "plan"
    # calcula el nro de materias OBLIGATORIAS por "carrera" y "plan"
    # Limpia el campo "plan" eliminando los finales como "2020.0" -> "2020" usando una expresion regular

    planes_materias = (
        planes[planes["obligatoria"] == "S"]
        .groupby(["carrera", "plan"], as_index=False, dropna=False)
        .size()
        .rename(columns={"size": "cant_materias"})
    )
    planes_materias["plan"] = (
        planes_materias["plan"].astype("string").str.replace(r"[.]0$", "", regex=True)
    )

    # Conversion del resultado en un vector con nombres
    # Convierte el data frame "planes_materias" en un vector con nombres, donde:
    # Los valores son las cantidades de materias (cant_materias).
    # Los nombres son combinaciones de carrera y plan, separadas por coma, como "Sistemas, 2020".

    planes_materias = planes_materias.set_index("plan")["cant_materias"]

    # Limpieza del campo "plan" en cursadas:
    # Esta línea modifica la columna plan del data frame cursadas
    # Usa sub() para reemplazar un patrón: si el contenido termina en ".0" (por ejemplo "2020.0"), lo reemplaza con una cadena vacía, es decir, lo elimina.
    # Resultado: "2020.0" → "2020".
    # Esto estandariza los valores del campo plan.
    # Lo mismo para finales

    cursadas["plan"] = (
        cursadas["plan"].astype("string").str.replace(r"[.]0$", "", regex=True)
    )
    finales["plan"] = (
        finales["plan"].astype("string").str.replace(r"[.]0$", "", regex=True)
    )
    cursadas["nota"] = pd.to_numeric(
        cursadas["nota"].astype("string").str.replace(",", ".", regex=False),
        errors="coerce",
    )
    finales["nota"] = pd.to_numeric(
        finales["nota"].astype("string").str.replace(",", ".", regex=False),
        errors="coerce",
    )

    # Indicadores de cursadas

    # Manipulación de datos uniendo los dataframes de alumnos y notas cursadas.
    # Las variables que nos interesa obtener son:
    # porcentaje de avance de cursadas
    # promedio de las notas obtenidas en el ultimo año
    # cantidad de materia que cursó en el ultimo año
    # materias aprobadas en total
    # materias promocionadas en total
    # materias recursadas

    # Agrupación y resumen de cursadas: Agrupa las cursadas por estudiante (id_alumno), carrera y plan. Luego calcula:
    # Cálculos por estudiantes
    # Cuenta cuántas materias fueron aprobadas
    cursadas["_cursada_aprobada"] = (cursadas["resultado"] == "A").astype(int)
    # Cuenta solo las aprobadas con final ("A").
    cursadas["_cursada_regular"] = (
        (cursadas["resultado"] == "A") & (cursadas["cond_regularidad"] == "Regular")
    ).astype(int)
    # Cuenta cuántas materias fueron promocionadas
    cursadas["_cursada_promocionada"] = (
        (cursadas["resultado"] == "A") & (cursadas["cond_regularidad"] == "Promocionó")
    ).astype(int)
    # Cuenta las cursadas desaprobadas: "U" (ausente) o "R" (reprobado).
    cursadas["_cursada_desaprobada"] = (
        cursadas["resultado"].isin(["U", "R"]).astype(int)
    )
    # Promedio de notas de las materias regularizadas durante el año 2023.
    _cursada_en_2023 = (cursadas["fecha_regularidad"] <= "2023-12-31") & (
        cursadas["fecha_regularidad"] >= "2023-01-01"
    )
    cursadas["_nota_cursada_ult_anio"] = cursadas["nota"].where(_cursada_en_2023)
    # Cantidad de materias únicas en las que el alumno se anotó (y obtuvo regularidad) en el año 2023.
    cursadas["_materia_anotada_ult_anio"] = cursadas["materia"].where(_cursada_en_2023)

    alumnos_con_cursadas = cursadas.groupby(
        ["id_alumno", "carrera", "plan"], as_index=False, dropna=False
    ).agg(
        cursadas_aprobadas=("_cursada_aprobada", "sum"),
        cursadas_regulares=("_cursada_regular", "sum"),
        cursadas_promocionadas=("_cursada_promocionada", "sum"),
        cursadas_desaprobadas=("_cursada_desaprobada", "sum"),
        notas_cursadas_ult_anio=("_nota_cursada_ult_anio", "mean"),
        materias_anotado_ult_anio=("_materia_anotada_ult_anio", "nunique"),
    )

    cursadas = cursadas.drop(
        columns=[
            "_cursada_aprobada",
            "_cursada_regular",
            "_cursada_promocionada",
            "_cursada_desaprobada",
            "_nota_cursada_ult_anio",
            "_materia_anotada_ult_anio",
        ]
    )

    # Calcula el porcentaje de materias aprobadas respecto al total
    alumnos_con_cursadas["porc_cursadas"] = alumnos_con_cursadas[
        "cursadas_aprobadas"
    ] / alumnos_con_cursadas["plan"].map(planes_materias)

    # Une los datos resumidos con el data frame alumnos, conservando todos los estudiantes (incluso si no tienen cursadas registradas). Esto se hace con un right join, donde la tabla "maestra" es alumnos.
    alumnos_con_cursadas = alumnos_con_cursadas.merge(
        alumnos_inscriptos[
            [
                "id_alumno",
                "carrera",
                "plan",
                "fecha_inscripcion",
                "localidad_nacimiento",
                "calidad",
            ]
        ],
        how="right",
        on=["id_alumno", "carrera", "plan"],
        suffixes=(".x", ".y"),
    )

    # Reemplaza con 0 los valores faltantes (NA) en los campos clave. Esto es útil para alumnos sin cursadas registradas.
    alumnos_con_cursadas = alumnos_con_cursadas.fillna(
        {
            "cursadas_aprobadas": 0,
            "cursadas_regulares": 0,
            "cursadas_promocionadas": 0,
            "cursadas_desaprobadas": 0,
            "materias_anotado_ult_anio": 0,
            "notas_cursadas_ult_anio": 0,
            "porc_cursadas": 0,
        }
    )

    # Indicadores de exámenes finales

    # Manipulacion de los datos uniendo los dataframes de alumnos y finales para
    # obtener la cantidad de finales rendidos, aprobados, desaprobados y rendidos en el último año
    # Agrupa los registros de finales por estudiante (id_alumno), carrera y plan.
    # Dentro del resumen se calculan varios indicadores:
    # finales_aprobados -> Cuenta la cantidad de finales aprobados ("A").
    finales["_final_aprobado"] = (finales["resultado"] == "A").astype(int)
    # finales_desaprobados -> Cuenta la cantidad de finales desaprobados ("R").
    finales["_final_desaprobado"] = (finales["resultado"] == "R").astype(int)
    # nota_finales_ult_anio -> Calcula el promedio de notas de finales posteriores al 1 de enero de 2023. Se omiten valores faltantes (NA) en el cálculo.
    finales["_nota_final_ult_anio"] = finales["nota"].where(
        finales["fecha"] > "2023-01-01"
    )
    # dias_dsd_ultimo_final -> Calcula la cantidad de días desde el último final rendido hasta la fecha actual.
    # Marca si la forma de aprobación fue equivalencia
    finales["cambio_plan"] = finales["forma_aprobacion"] == "Equivalencia"

    alumnos_con_finales = finales.groupby(
        ["id_alumno", "carrera", "plan"], as_index=False, dropna=False
    ).agg(
        finales_aprobados=("_final_aprobado", "sum"),
        finales_desaprobados=("_final_desaprobado", "sum"),
        nota_finales_ult_anio=("_nota_final_ult_anio", "mean"),
        _fecha_ultimo_final=("fecha", "max"),
        # cambio_plan se usa para saber si el alumno cambio de plan,
        # y asi contar los finales aprobados como equivalencia también como cursadas aprobadas
        cambio_plan=("cambio_plan", "any"),
    )

    _fecha_actual = pd.Timestamp(
        os.environ["ANALYSIS_DATE"]
        if os.environ.get("ANALYSIS_DATE")
        else pd.Timestamp.today()
    ).normalize()
    alumnos_con_finales["dias_dsd_ultimo_final"] = _fecha_actual - pd.to_datetime(
        alumnos_con_finales["_fecha_ultimo_final"]
    )
    alumnos_con_finales = alumnos_con_finales.drop(columns=["_fecha_ultimo_final"])

    finales = finales.drop(
        columns=["_final_aprobado", "_final_desaprobado", "_nota_final_ult_anio"]
    )

    # Unión con el data frame alumnos -> Hace una unión por derecha (right join) para mantener todos los estudiantes, incluso si no tienen finales registrados.
    alumnos_con_finales = alumnos_con_finales.merge(
        alumnos_inscriptos[["id_alumno", "carrera", "plan", "fecha_inscripcion"]],
        how="right",
        on=["id_alumno", "carrera", "plan"],
        suffixes=(".x", ".y"),
    )

    # Reemplazo de valores faltantes. Completa con ceros los campos faltantes (NA), útil para estudiantes sin finales registrados.
    _dias_desde_inscripcion = _fecha_actual - pd.to_datetime(
        alumnos_con_finales["fecha_inscripcion"]
    )
    alumnos_con_finales["dias_dsd_ultimo_final"] = alumnos_con_finales[
        "dias_dsd_ultimo_final"
    ].fillna(_dias_desde_inscripcion)
    alumnos_con_finales["cambio_plan"] = alumnos_con_finales["cambio_plan"].fillna(
        False
    )
    alumnos_con_finales = alumnos_con_finales.fillna(
        {
            "finales_aprobados": 0,
            "finales_desaprobados": 0,
            "nota_finales_ult_anio": 0,
        }
    )
    alumnos_con_finales = alumnos_con_finales.drop(columns=["fecha_inscripcion"])

    # Consolidación de indicadores por estudiante

    # unión de los dataframes para obtener un dataframe central

    # Calcular tiempo desde el ingreso.
    # Agrega una nueva columna tiempo_desde_ingreso, que indica cuántos días han pasado desde que el estudiante ingresó.
    alumnos_cursadas_finales = alumnos.copy()
    alumnos_cursadas_finales["tiempo_desde_ingreso"] = _fecha_actual - pd.to_datetime(
        alumnos_cursadas_finales["fecha_inscripcion"]
    )

    # Selección de columnas clave: Se conservan solo los identificadores del alumno y la nueva columna tiempo_desde_ingreso.
    alumnos_cursadas_finales = alumnos_cursadas_finales[
        ["id_alumno", "carrera", "plan", "tiempo_desde_ingreso"]
    ]

    # Uniones internas (inner joins)
    # Se unen los tres data frames por carrera y plan.
    # Como son inner_join, solo se conservarán los estudiantes que están presentes en los tres data frames (es decir, los que tienen cursadas y finales registrados, además de estar en alumnos).
    alumnos_cursadas_finales = alumnos_cursadas_finales.merge(
        alumnos_con_cursadas,
        how="inner",
        on=["id_alumno", "carrera", "plan"],
        suffixes=(".x", ".y"),
    )
    alumnos_cursadas_finales = alumnos_cursadas_finales.merge(
        alumnos_con_finales,
        how="inner",
        on=["id_alumno", "carrera", "plan"],
        suffixes=(".x", ".y"),
    )

    # total_materias_finalizadas: suma de finales aprobados y materias promocionadas (que no necesitan final).
    # porc_finales: porcentaje del plan completo que representa esa suma, dividiendo por el total de materias (materias_sistemas, que vale 44) + 1.
    # Posiblemente se suma 1 para ajustar por alguna materia adicional no contabilizada o por un error conocido del dataset.
    # relacion_finales_cursadas: mide qué proporción de las materias cursadas fueron finalizadas (ya sea con final o promoción).
    alumnos_cursadas_finales["cursadas_aprobadas"] = np.where(
        alumnos_cursadas_finales["cambio_plan"] == True,
        alumnos_cursadas_finales["finales_aprobados"],
        alumnos_cursadas_finales["cursadas_aprobadas"],
    )
    alumnos_cursadas_finales["cursadas_regulares"] = np.where(
        alumnos_cursadas_finales["cambio_plan"] == True,
        alumnos_cursadas_finales["cursadas_aprobadas"],
        alumnos_cursadas_finales["cursadas_regulares"],
    )
    alumnos_cursadas_finales["cursadas_desaprobadas"] = np.where(
        alumnos_cursadas_finales["cambio_plan"] == True,
        alumnos_cursadas_finales["finales_desaprobados"],
        alumnos_cursadas_finales["cursadas_desaprobadas"],
    )
    alumnos_cursadas_finales["total_materias_finalizadas"] = alumnos_cursadas_finales[
        "finales_aprobados"
    ]
    alumnos_cursadas_finales["porc_finales"] = alumnos_cursadas_finales[
        "total_materias_finalizadas"
    ] / alumnos_cursadas_finales["plan"].map(planes_materias)
    alumnos_cursadas_finales["porc_cursadas"] = np.where(
        alumnos_cursadas_finales["cambio_plan"] == True,
        alumnos_cursadas_finales["porc_finales"],
        alumnos_cursadas_finales["porc_cursadas"],
    )
    alumnos_cursadas_finales["relacion_finales_cursadas"] = np.where(
        alumnos_cursadas_finales["cursadas_aprobadas"] == 0,
        np.nan,
        alumnos_cursadas_finales["total_materias_finalizadas"]
        / alumnos_cursadas_finales["cursadas_aprobadas"],
    )

    # Para eliminar filas repetidas de alumnos_cursadas_finales. Tal vez convenga hacerlo directamente sobre alumnos
    alumnos_cursadas_finales = alumnos_cursadas_finales.drop_duplicates().copy()
    alumnos_cursadas_finales = alumnos_cursadas_finales.drop_duplicates(
        subset=["id_alumno"], keep="first"
    ).copy()

    # Población de análisis y condición de deserción

    # filtro para obtener un dataframe con aquellos que tengan menos del 50 % de la carrera avanzada y donde se marca la deserción
    alumnos_s_avanzados = alumnos_cursadas_finales[
        alumnos_cursadas_finales["porc_finales"] <= 0.5
    ].copy()

    # Filtrar alumnos con avance ≤ 50%: Conserva solo los estudiantes que han finalizado como máximo el 50% del plan (entre finales aprobados y materias promocionadas).
    # Detección de deserción
    # Se crea una nueva columna lógica llamada deserto que vale TRUE si se cumplen ambas condiciones:
    # 1) Pasaron más de 2 años (730 días) desde que rindió su último final.
    # 2) El estudiante no se anotó a ninguna materia en el último año (año 2023, según los datos usados antes).
    alumnos_s_avanzados["deserto"] = (
        (alumnos_s_avanzados["dias_dsd_ultimo_final"] > pd.Timedelta(days=730))
        & (alumnos_s_avanzados["materias_anotado_ult_anio"] == 0)
    ) | (alumnos_s_avanzados["calidad"] == "Abandono")

    # Lo mismo que arriba, pero para los alumnos que desaprobaron alguna materia de las importantes
    alumnos_desaprob_mat_IS = alumnos_desaprob_mat_IS.merge(
        alumnos_cursadas_finales,
        how="inner",
        on=["id_alumno", "plan", "carrera", "fecha_inscripcion"],
        suffixes=(".x", ".y"),
    )

    alumnos_s_avanzados_desaprob_mat_IS = alumnos_desaprob_mat_IS.drop(
        columns=["fecha_inscripcion"]
    ).copy()
    alumnos_s_avanzados_desaprob_mat_IS = alumnos_s_avanzados_desaprob_mat_IS[
        alumnos_s_avanzados_desaprob_mat_IS["porc_finales"] <= 0.5
    ].copy()
    alumnos_s_avanzados_desaprob_mat_IS["deserto"] = (
        (
            alumnos_s_avanzados_desaprob_mat_IS["dias_dsd_ultimo_final"]
            > pd.Timedelta(days=730)
        )
        & (alumnos_s_avanzados_desaprob_mat_IS["materias_anotado_ult_anio"] == 0)
    ) | (alumnos_s_avanzados_desaprob_mat_IS["calidad.x"] == "Abandono")

    # Separación de alumnos desertores
    alumnos_desertores = alumnos_s_avanzados[
        alumnos_s_avanzados["deserto"] == True
    ].copy()

    # Entregar los datos directamente a la siguiente etapa.
    return {
        "fecha_analisis": _fecha_actual.date().isoformat(),
        "alumnos_s_avanzados": alumnos_s_avanzados,
        "alumnos_s_avanzados_desaprob_mat_IS": alumnos_s_avanzados_desaprob_mat_IS,
        "alumnos_desertores": alumnos_desertores,
    }


if __name__ == "__main__":
    main()
