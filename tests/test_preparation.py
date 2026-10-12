"""Validate column contracts together with input alignment."""

import pandas as pd
import pytest
from pandera.errors import SchemaError, SchemaErrors

from src.data.constants import Columns
from src.data.preparation import prepare_input, validate_input
from src.data.schemas import AcademicData, ClusteringInput


def test_prepare_input_loads_data_for_requested_date(
    entry: ClusteringInput, monkeypatch: pytest.MonkeyPatch
) -> None:
    students = entry["original_values"].copy()
    for column in (Columns.DAYS_SINCE_ENROLLMENT, Columns.DAYS_SINCE_LAST_FINAL):
        students[column] = pd.to_timedelta(students[column], unit="D")
    students[Columns.STUDENT_ID] = entry["student_ids"]
    for column in (
        Columns.LAST_YEAR_FINAL_GRADE,
        Columns.REGULAR_COURSES,
        Columns.LAST_YEAR_COURSE_GRADE,
        Columns.FINALS_TO_COURSES_RATIO,
        Columns.COURSE_COMPLETION_RATIO,
        Columns.COMPLETED_SUBJECTS,
        Columns.BIRTHPLACE,
        Columns.ENROLLMENT_DATE,
        Columns.CURRICULUM_CHANGE,
        Columns.CURRICULUM,
        Columns.DEGREE,
        Columns.ACADEMIC_STATUS,
    ):
        students[column] = 0
    calls = []

    def prepare_academic_data(*, analysis_date: str) -> AcademicData:
        calls.append(analysis_date)
        return {
            "eligible_students": students,
            "analysis_date": analysis_date,
            "eligible_core_subject_students": students.iloc[:0],
            "dropout_students": students.iloc[:0],
        }

    monkeypatch.setattr(
        "src.data.preparation.prepare_academic_data", prepare_academic_data
    )
    result = prepare_input(analysis_date="2026-10-01")
    assert calls == ["2026-10-01"]
    assert result["analysis_date"] == "2026-10-01"
    pd.testing.assert_frame_equal(result["original_values"], entry["original_values"])
    pd.testing.assert_frame_equal(result["matrix"], entry["matrix"])


def test_schemas_preserve_values_and_allow_standardized_dropout(
    entry: ClusteringInput,
) -> None:
    original_values = entry["original_values"].copy()
    matrix = entry["matrix"].copy()
    assert not entry["matrix"][Columns.DROPPED_OUT].isin([0, 1]).all()
    validate_input(entry)
    pd.testing.assert_frame_equal(entry["original_values"], original_values)
    pd.testing.assert_frame_equal(entry["matrix"], matrix)


@pytest.mark.parametrize("change", ["missing", "extra", "order", "type"])
def test_rejects_invalid_schema_even_when_both_tables_match(
    entry: ClusteringInput, change: str
) -> None:
    for field in ("original_values", "matrix"):
        table = entry[field]
        if change == "missing":
            table = table.drop(columns=Columns.PASSED_COURSES)
        elif change == "extra":
            table = table.assign(variable_extra=1.0)
        elif change == "order":
            table = table[table.columns[::-1]]
        else:
            table = table.astype({Columns.PASSED_FINALS: str})
        entry[field] = table
    with pytest.raises((SchemaError, SchemaErrors)):
        validate_input(entry)


@pytest.mark.parametrize("value", [2.0, float("nan")])
def test_rejects_invalid_original_dropout(entry: ClusteringInput, value: float) -> None:
    entry["original_values"].loc[0, Columns.DROPPED_OUT] = value
    with pytest.raises(SchemaError):
        validate_input(entry)
