"""Clustering input column contracts, in the original analysis order."""

from typing import TypedDict

import numpy as np
import pandas as pd
import pandera.pandas as pa
from numpy.typing import NDArray
from pandera.typing import DataFrame, Series

from src.data.constants import Columns


class OriginalVariables(pa.DataFrameModel):
    """Unscaled indicators; counts are stored as float64."""

    days_since_enrollment: Series[float] = pa.Field(
        alias=Columns.DAYS_SINCE_ENROLLMENT, description="Days since enrollment."
    )
    passed_courses: Series[float] = pa.Field(
        alias=Columns.PASSED_COURSES, description="Number of passed courses."
    )
    promoted_courses: Series[float] = pa.Field(
        alias=Columns.PROMOTED_COURSES,
        description="Number of promoted courses.",
    )
    failed_courses: Series[float] = pa.Field(
        alias=Columns.FAILED_COURSES, description="Number of failed courses."
    )
    last_year_subjects: Series[float] = pa.Field(
        alias=Columns.LAST_YEAR_SUBJECTS,
        description="Distinct subjects with enrollment records in the last year.",
    )
    passed_finals: Series[float] = pa.Field(
        alias=Columns.PASSED_FINALS, description="Number of passed final exams."
    )
    failed_finals: Series[float] = pa.Field(
        alias=Columns.FAILED_FINALS, description="Number of failed final exams."
    )
    days_since_last_final: Series[float] = pa.Field(
        alias=Columns.DAYS_SINCE_LAST_FINAL,
        description="Days since the last final exam, or enrollment if no final is recorded.",
    )
    final_completion_ratio: Series[float] = pa.Field(
        alias=Columns.FINAL_COMPLETION_RATIO,
        description="Passed final exams divided by the curriculum subject count.",
    )
    dropped_out: Series[float] = pa.Field(
        alias=Columns.DROPPED_OUT,
        isin=[0.0, 1.0],
        description="Dropout indicator: 0 or 1.",
    )

    class Config:
        strict = True
        ordered = True


class StandardizedVariables(pa.DataFrameModel):
    """Original columns standardized to mean zero and sample deviation one.

    Every feature, including the dropout indicator, is standardized.
    validate_input checks alignment with the original values."""

    days_since_enrollment: Series[float] = pa.Field(alias=Columns.DAYS_SINCE_ENROLLMENT)
    passed_courses: Series[float] = pa.Field(alias=Columns.PASSED_COURSES)
    promoted_courses: Series[float] = pa.Field(alias=Columns.PROMOTED_COURSES)
    failed_courses: Series[float] = pa.Field(alias=Columns.FAILED_COURSES)
    last_year_subjects: Series[float] = pa.Field(alias=Columns.LAST_YEAR_SUBJECTS)
    passed_finals: Series[float] = pa.Field(alias=Columns.PASSED_FINALS)
    failed_finals: Series[float] = pa.Field(alias=Columns.FAILED_FINALS)
    days_since_last_final: Series[float] = pa.Field(alias=Columns.DAYS_SINCE_LAST_FINAL)
    final_completion_ratio: Series[float] = pa.Field(
        alias=Columns.FINAL_COMPLETION_RATIO
    )
    dropped_out: Series[float] = pa.Field(alias=Columns.DROPPED_OUT)

    class Config:
        strict = True
        ordered = True


class ClusteringInput(TypedDict):
    """Tables and student identifiers aligned by position, not by pandas index."""

    original_values: DataFrame[OriginalVariables]
    matrix: DataFrame[StandardizedVariables]
    student_ids: NDArray[np.int64]
    analysis_date: str


class AcademicData(TypedDict):
    """Prepared tables; provides typing without validating the raw CSV files."""

    analysis_date: str
    eligible_students: pd.DataFrame
    eligible_core_subject_students: pd.DataFrame
    dropout_students: pd.DataFrame
