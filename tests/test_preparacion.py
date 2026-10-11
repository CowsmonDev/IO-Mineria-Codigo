"""El esquema de columnas se comprueba junto con la alineación de la entrada."""

import pandas as pd
import pytest
from pandera.errors import SchemaError, SchemaErrors

from src.data.preparacion import preparar_entrada, validar_entrada


def test_preparar_entrada_carga_datos_con_la_fecha_solicitada(entrada, monkeypatch):
    alumnos = entrada["originales"].copy()
    for columna in ("tiempo_desde_ingreso", "dias_dsd_ultimo_final"):
        alumnos[columna] = pd.to_timedelta(alumnos[columna], unit="D")
    alumnos["id_alumno"] = entrada["ids_alumnos"]
    for columna in (
        "nota_finales_ult_anio",
        "cursadas_regulares",
        "notas_cursadas_ult_anio",
        "relacion_finales_cursadas",
        "porc_cursadas",
        "total_materias_finalizadas",
        "localidad_nacimiento",
        "fecha_inscripcion",
        "cambio_plan",
        "plan",
        "carrera",
        "calidad",
    ):
        alumnos[columna] = 0
    llamadas = []

    def preparar_datos_academicos(*, fecha_analisis):
        llamadas.append(fecha_analisis)
        return {"alumnos_s_avanzados": alumnos, "fecha_analisis": fecha_analisis}

    monkeypatch.setattr(
        "src.data.preparacion.preparar_datos_academicos", preparar_datos_academicos
    )
    resultado = preparar_entrada(fecha_analisis="2026-10-01")
    assert llamadas == ["2026-10-01"]
    assert resultado["fecha_analisis"] == "2026-10-01"
    pd.testing.assert_frame_equal(resultado["originales"], entrada["originales"])
    pd.testing.assert_frame_equal(resultado["matriz"], entrada["matriz"])


def test_esquemas_conservan_valores_y_permiten_deserto_estandarizado(entrada):
    originales = entrada["originales"].copy()
    matriz = entrada["matriz"].copy()
    assert not entrada["matriz"]["deserto"].isin([0, 1]).all()
    validar_entrada(entrada)
    pd.testing.assert_frame_equal(entrada["originales"], originales)
    pd.testing.assert_frame_equal(entrada["matriz"], matriz)


@pytest.mark.parametrize("cambio", ["faltante", "extra", "orden", "tipo"])
def test_rechaza_esquema_incorrecto_aunque_ambas_tablas_coincidan(entrada, cambio):
    for campo in ("originales", "matriz"):
        tabla = entrada[campo]
        if cambio == "faltante":
            tabla = tabla.drop(columns="cursadas_aprobadas")
        elif cambio == "extra":
            tabla = tabla.assign(variable_extra=1.0)
        elif cambio == "orden":
            tabla = tabla[tabla.columns[::-1]]
        else:
            tabla = tabla.astype({"finales_aprobados": str})
        entrada[campo] = tabla
    with pytest.raises((SchemaError, SchemaErrors)):
        validar_entrada(entrada)


@pytest.mark.parametrize("valor", [2.0, float("nan")])
def test_rechaza_deserto_original_invalido(entrada, valor):
    entrada["originales"].loc[0, "deserto"] = valor
    with pytest.raises(SchemaError):
        validar_entrada(entrada)
