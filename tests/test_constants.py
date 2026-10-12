"""English identifiers retain original source names and categories."""

from io import StringIO

import pandas as pd

from src.data.constants import AcademicStatus, Columns
from src.data.schemas import ClusteringInput, OriginalVariables, StandardizedVariables


def test_constants_filter_original_csv_categories() -> None:
    students = pd.read_csv(
        StringIO("id_alumno|calidad\n1|Abandono\n2|Egreso\n"), sep="|"
    )
    selected = students.loc[
        students[Columns.ACADEMIC_STATUS] == AcademicStatus.DROPOUT,
        Columns.STUDENT_ID,
    ]
    assert selected.tolist() == [1]
    assert students.columns.tolist() == ["id_alumno", "calidad"]


def test_english_schema_fields_keep_original_column_contract(
    entry: ClusteringInput,
) -> None:
    expected = [
        "tiempo_desde_ingreso",
        "cursadas_aprobadas",
        "cursadas_promocionadas",
        "cursadas_desaprobadas",
        "materias_anotado_ult_anio",
        "finales_aprobados",
        "finales_desaprobados",
        "dias_dsd_ultimo_final",
        "porc_finales",
        "deserto",
    ]
    assert list(OriginalVariables.to_schema().columns) == expected
    assert list(StandardizedVariables.to_schema().columns) == expected
    assert "dropped_out" in OriginalVariables.__annotations__
    validated = OriginalVariables.validate(entry["original_values"])
    pd.testing.assert_frame_equal(validated, entry["original_values"])
