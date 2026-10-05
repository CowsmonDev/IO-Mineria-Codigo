"""El esquema de columnas se comprueba junto con la alineación de la entrada."""

import pandas as pd
import pytest
from pandera.errors import SchemaError, SchemaErrors

from src.data.preparacion import validar_entrada


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
