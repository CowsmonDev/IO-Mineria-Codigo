"""Prepare features while preserving the original standardization."""

import numpy as np
import pandas as pd
from pandera.typing import DataFrame

from src.data.constants import Columns
from src.data.processing import prepare_academic_data
from src.data.schemas import (
    ClusteringInput,
    OriginalVariables,
    StandardizedVariables,
)


def prepare_variables(students: pd.DataFrame) -> DataFrame[OriginalVariables]:
    """Convert durations to days and select features without changing the input."""
    eligible_students = students.copy()
    eligible_students[Columns.DAYS_SINCE_ENROLLMENT] = (
        eligible_students[Columns.DAYS_SINCE_ENROLLMENT].dt.total_seconds() / 86400
    )
    eligible_students[Columns.DROPPED_OUT] = eligible_students[
        Columns.DROPPED_OUT
    ].astype(float)
    eligible_students[Columns.DAYS_SINCE_LAST_FINAL] = (
        eligible_students[Columns.DAYS_SINCE_LAST_FINAL].dt.total_seconds() / 86400
    )

    eligible_students = eligible_students.drop(
        columns=[
            Columns.LAST_YEAR_FINAL_GRADE,
            Columns.REGULAR_COURSES,
            Columns.LAST_YEAR_COURSE_GRADE,
            Columns.FINALS_TO_COURSES_RATIO,
            Columns.COURSE_COMPLETION_RATIO,
            Columns.COMPLETED_SUBJECTS,
            Columns.BIRTHPLACE,
            Columns.ENROLLMENT_DATE,
            Columns.CURRICULUM_CHANGE,
            Columns.STUDENT_ID,
            Columns.CURRICULUM,
            Columns.DEGREE,
            Columns.ACADEMIC_STATUS,
        ]
    )

    return OriginalVariables.validate(eligible_students)


def standardize(
    eligible_students: DataFrame[OriginalVariables],
) -> DataFrame[StandardizedVariables]:
    """Standardize using the sample deviation while preserving the original values.

    Includes the dropout indicator as in the original input.
    Clustering labels are added after this step."""
    standardized_students = (
        eligible_students - eligible_students.mean(axis=0)
    ) / eligible_students.std(axis=0, ddof=1)
    standardized_students.index = np.arange(1, len(standardized_students) + 1)

    return standardized_students


def prepare_input(
    *, analysis_date: str | pd.Timestamp | None = None
) -> ClusteringInput:
    """Load data and prepare identities, original values and the unlabeled matrix."""
    data = prepare_academic_data(analysis_date=analysis_date)
    students = data["eligible_students"]
    original_values = prepare_variables(students).reset_index(drop=True)
    entry: ClusteringInput = {
        "original_values": original_values,
        "matrix": standardize(original_values),
        "student_ids": students[Columns.STUDENT_ID].to_numpy(copy=True),
        "analysis_date": data["analysis_date"],
    }
    validate_input(entry)
    return entry


def validate_input(entry: ClusteringInput) -> None:
    """Reject label contamination, invalid identifiers and misaligned rows."""
    original_values, matrix = entry["original_values"], entry["matrix"]
    ids = np.asarray(entry["student_ids"])
    if any(str(col).startswith("cluster") for col in matrix.columns):
        raise ValueError("Clustering labels must not be included in the input.")
    if list(original_values.columns) != list(matrix.columns):
        raise ValueError("Original and standardized features do not match.")
    if len(original_values) != len(matrix) or len(ids) != len(matrix):
        raise ValueError("Tables and identifiers must have the same length.")
    if pd.isna(ids).any() or pd.Series(ids).duplicated().any():
        raise ValueError("Each row must have a unique, non-null student identifier.")
    OriginalVariables.validate(original_values)
    StandardizedVariables.validate(matrix)
    if not np.isfinite(matrix.to_numpy(dtype=float)).all():
        raise ValueError("The input contains missing or non-finite values.")
    expected = (original_values - original_values.mean()) / original_values.std(ddof=1)
    if not np.allclose(matrix.to_numpy(), expected.to_numpy(), rtol=1e-10, atol=1e-10):
        raise ValueError(
            "The input does not preserve the original order and standardization."
        )
