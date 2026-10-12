"""Load academic CSV files, filter students and compute indicators."""

import os
from pathlib import Path

import numpy as np
import pandas as pd

from src.data.constants import (
    AcademicStatus,
    ApprovalMethod,
    Columns,
    CoreSubjects,
    CourseStatus,
    RequiredSubject,
    ResultCode,
)
from src.data.schemas import AcademicData


def prepare_academic_data(
    analysis_date: str | pd.Timestamp | None = None,
) -> AcademicData:
    """Load data and return student populations with their academic indicators."""
    data_directory = Path(__file__).resolve().parents[2] / "data"

    # Imports and data loading.

    # Load SIU Guarani student, course, final-exam and curriculum records.

    students = pd.read_csv(data_directory / "001_alumnos.csv", header=0, sep="|")

    courses = pd.read_csv(
        data_directory / "002_regularidades.csv",
        sep="|",
        dtype={Columns.SUBJECT_CODE: str},
    )

    finals = pd.read_csv(
        data_directory / "003_historia_academica.csv",
        sep="|",
        dtype={Columns.SUBJECT_CODE: str},
    )

    curricula = pd.read_csv(
        data_directory / "000_materias_planes.csv",
        sep="|",
        dtype={Columns.SUBJECT_CODE: str},
    )

    # Student and subject selection.

    # Select Systems Engineering (206) students enrolled after 2011-01-01
    # and before 2023-12-31, retaining the original date boundaries.
    students = students[
        (students[Columns.ENROLLMENT_DATE] > "2011-01-01")
        & (students[Columns.ENROLLMENT_DATE] < "2023-12-31")
        & (students[Columns.DEGREE] == 206)
        & (students[Columns.ACADEMIC_STATUS] != AcademicStatus.GRADUATED)
    ].copy()

    # Exclude the exchange student omitted by the original analysis.
    enrolled_students = students[students[Columns.STUDENT_ID] != 109662].copy()

    # Exclude internships, elective subjects and final projects from curricula.
    curricula = curricula[
        (curricula[Columns.DEGREE] == 206)
        & (curricula[Columns.REQUIRED_SUBJECT] == RequiredSubject.YES)
        & (~curricula[Columns.SUBJECT_CODE].isin(["0205", "6523", "PPS"]))
    ].copy()

    courses = courses[courses[Columns.DEGREE] == 206].copy()

    courses = courses.merge(
        curricula,
        how="inner",
        on=[
            Columns.CURRICULUM,
            Columns.DEGREE,
            Columns.SUBJECT_CODE,
            Columns.SUBJECT_NAME,
        ],
        suffixes=(".x", ".y"),
    )

    finals = finals[
        (finals[Columns.DEGREE] == 206)
        & (~finals[Columns.SUBJECT_CODE].isin(["PPS", "P0001", "P0002", "0205"]))
    ].copy()

    finals = finals.merge(
        curricula,
        how="inner",
        on=[
            Columns.CURRICULUM,
            Columns.DEGREE,
            Columns.SUBJECT_CODE,
            Columns.SUBJECT_NAME,
        ],
        suffixes=(".x", ".y"),
    )

    # Remove duplicate student records.
    enrolled_students = enrolled_students.drop_duplicates().copy()
    enrolled_students = enrolled_students.drop_duplicates(
        subset=[Columns.STUDENT_ID], keep="first"
    ).copy()

    # Students who failed core subjects.

    # Identify students with failed or absent results in the selected core subjects.

    students_with_failed_core_subjects = enrolled_students.merge(
        courses,
        how="inner",
        on=[Columns.STUDENT_ID, Columns.CURRICULUM, Columns.DEGREE],
        suffixes=(".x", ".y"),
    )
    students_with_failed_core_subjects = students_with_failed_core_subjects[
        students_with_failed_core_subjects[Columns.SUBJECT_NAME].isin(
            [
                CoreSubjects.INTRO_PROGRAMMING_I,
                CoreSubjects.INTRO_PROGRAMMING_II,
                CoreSubjects.ALGORITHMS_I,
                CoreSubjects.ALGORITHMS_II,
                CoreSubjects.OBJECT_ORIENTED_PROGRAMMING,
            ]
        )
        & students_with_failed_core_subjects[Columns.RESULT].isin(
            [ResultCode.FAILED, ResultCode.ABSENT]
        )
    ].copy()
    students_with_failed_core_subjects = (
        students_with_failed_core_subjects.drop_duplicates(
            subset=[Columns.STUDENT_ID, Columns.DEGREE, Columns.CURRICULUM],
            keep="first",
        ).copy()
    )

    # Curriculum fields and normalization.

    # Count required subjects by degree and curriculum.
    # Normalize curriculum identifiers by removing trailing .0.

    curriculum_subject_counts = (
        curricula[curricula[Columns.REQUIRED_SUBJECT] == RequiredSubject.YES]
        .groupby([Columns.DEGREE, Columns.CURRICULUM], as_index=False, dropna=False)
        .size()
        .rename(columns={"size": Columns.SUBJECT_COUNT})
    )
    curriculum_subject_counts[Columns.CURRICULUM] = (
        curriculum_subject_counts[Columns.CURRICULUM]
        .astype("string")
        .str.replace("[.]0$", "", regex=True)
    )

    # Build the curriculum-to-subject-count lookup.

    curriculum_subject_counts = curriculum_subject_counts.set_index(Columns.CURRICULUM)[
        Columns.SUBJECT_COUNT
    ]

    # Normalize curriculum identifiers in course and final-exam records.

    courses[Columns.CURRICULUM] = (
        courses[Columns.CURRICULUM]
        .astype("string")
        .str.replace("[.]0$", "", regex=True)
    )
    finals[Columns.CURRICULUM] = (
        finals[Columns.CURRICULUM].astype("string").str.replace("[.]0$", "", regex=True)
    )
    courses[Columns.GRADE] = pd.to_numeric(
        courses[Columns.GRADE].astype("string").str.replace(",", ".", regex=False),
        errors="coerce",
    )
    finals[Columns.GRADE] = pd.to_numeric(
        finals[Columns.GRADE].astype("string").str.replace(",", ".", regex=False),
        errors="coerce",
    )

    # Course indicators.

    # Compute course progress, recent grades and activity,
    # and counts of passed, promoted and failed course records.

    # Compute per-student indicators grouped by student, degree and curriculum.
    courses[Columns.COURSE_PASSED_FLAG] = (
        courses[Columns.RESULT] == ResultCode.PASSED
    ).astype(int)
    # Count passed course records with regular completion status.
    courses[Columns.COURSE_REGULAR_FLAG] = (
        (courses[Columns.RESULT] == ResultCode.PASSED)
        & (courses[Columns.COURSE_STATUS] == CourseStatus.REGULAR)
    ).astype(int)
    # Count course records approved through promotion.
    courses[Columns.COURSE_PROMOTED_FLAG] = (
        (courses[Columns.RESULT] == ResultCode.PASSED)
        & (courses[Columns.COURSE_STATUS] == CourseStatus.PROMOTED)
    ).astype(int)
    # Count absent (U) and failed (R) course records.
    courses[Columns.COURSE_FAILED_FLAG] = (
        courses[Columns.RESULT].isin([ResultCode.ABSENT, ResultCode.FAILED]).astype(int)
    )
    # Mean grades for course records dated within 2023.
    _course_in_2023 = (courses[Columns.COURSE_RECORD_DATE] <= "2023-12-31") & (
        courses[Columns.COURSE_RECORD_DATE] >= "2023-01-01"
    )
    courses[Columns.LAST_YEAR_COURSE_GRADE_TEMP] = courses[Columns.GRADE].where(
        _course_in_2023
    )
    # Count distinct subjects with course records dated within 2023.
    courses[Columns.LAST_YEAR_SUBJECT_TEMP] = courses[Columns.SUBJECT_CODE].where(
        _course_in_2023
    )

    students_with_courses = courses.groupby(
        [Columns.STUDENT_ID, Columns.DEGREE, Columns.CURRICULUM],
        as_index=False,
        dropna=False,
    ).agg(
        **{
            Columns.PASSED_COURSES: (Columns.COURSE_PASSED_FLAG, "sum"),
            Columns.REGULAR_COURSES: (Columns.COURSE_REGULAR_FLAG, "sum"),
            Columns.PROMOTED_COURSES: (Columns.COURSE_PROMOTED_FLAG, "sum"),
            Columns.FAILED_COURSES: (Columns.COURSE_FAILED_FLAG, "sum"),
            Columns.LAST_YEAR_COURSE_GRADE: (
                Columns.LAST_YEAR_COURSE_GRADE_TEMP,
                "mean",
            ),
            Columns.LAST_YEAR_SUBJECTS: (Columns.LAST_YEAR_SUBJECT_TEMP, "nunique"),
        },
    )

    courses = courses.drop(
        columns=[
            Columns.COURSE_PASSED_FLAG,
            Columns.COURSE_REGULAR_FLAG,
            Columns.COURSE_PROMOTED_FLAG,
            Columns.COURSE_FAILED_FLAG,
            Columns.LAST_YEAR_COURSE_GRADE_TEMP,
            Columns.LAST_YEAR_SUBJECT_TEMP,
        ]
    )

    # Compute the fraction of passed courses in the curriculum.
    students_with_courses[Columns.COURSE_COMPLETION_RATIO] = students_with_courses[
        Columns.PASSED_COURSES
    ] / students_with_courses[Columns.CURRICULUM].map(curriculum_subject_counts)

    # Right-join onto students so those without course records are retained.
    students_with_courses = students_with_courses.merge(
        enrolled_students[
            [
                Columns.STUDENT_ID,
                Columns.DEGREE,
                Columns.CURRICULUM,
                Columns.ENROLLMENT_DATE,
                Columns.BIRTHPLACE,
                Columns.ACADEMIC_STATUS,
            ]
        ],
        how="right",
        on=[Columns.STUDENT_ID, Columns.DEGREE, Columns.CURRICULUM],
        suffixes=(".x", ".y"),
    )

    # Fill missing course indicators with zero for students without records.
    students_with_courses = students_with_courses.fillna(
        {
            Columns.PASSED_COURSES: 0,
            Columns.REGULAR_COURSES: 0,
            Columns.PROMOTED_COURSES: 0,
            Columns.FAILED_COURSES: 0,
            Columns.LAST_YEAR_SUBJECTS: 0,
            Columns.LAST_YEAR_COURSE_GRADE: 0,
            Columns.COURSE_COMPLETION_RATIO: 0,
        }
    )

    # Final-exam indicators.

    # Group final-exam records by student, degree and curriculum.
    # Count passed final exams (A).
    finals[Columns.FINAL_PASSED_FLAG] = (
        finals[Columns.RESULT] == ResultCode.PASSED
    ).astype(int)
    # Count failed final exams (R).
    finals[Columns.FINAL_FAILED_FLAG] = (
        finals[Columns.RESULT] == ResultCode.FAILED
    ).astype(int)
    # Mean final-exam grades after 2023-01-01, excluding missing grades.
    finals[Columns.LAST_YEAR_FINAL_GRADE_TEMP] = finals[Columns.GRADE].where(
        finals[Columns.EXAM_DATE] > "2023-01-01"
    )
    # Mark curriculum changes inferred from equivalence approvals.
    finals[Columns.CURRICULUM_CHANGE] = (
        finals[Columns.APPROVAL_METHOD] == ApprovalMethod.EQUIVALENCE
    )

    students_with_finals = finals.groupby(
        [Columns.STUDENT_ID, Columns.DEGREE, Columns.CURRICULUM],
        as_index=False,
        dropna=False,
    ).agg(
        **{
            Columns.PASSED_FINALS: (Columns.FINAL_PASSED_FLAG, "sum"),
            Columns.FAILED_FINALS: (Columns.FINAL_FAILED_FLAG, "sum"),
            Columns.LAST_YEAR_FINAL_GRADE: (Columns.LAST_YEAR_FINAL_GRADE_TEMP, "mean"),
            Columns.LAST_FINAL_DATE: (Columns.EXAM_DATE, "max"),
            Columns.CURRICULUM_CHANGE: (Columns.CURRICULUM_CHANGE, "any"),
        },
    )

    _analysis_date = pd.Timestamp(
        analysis_date or os.environ.get("ANALYSIS_DATE") or pd.Timestamp.today()
    ).normalize()
    students_with_finals[Columns.DAYS_SINCE_LAST_FINAL] = (
        _analysis_date - pd.to_datetime(students_with_finals[Columns.LAST_FINAL_DATE])
    )
    students_with_finals = students_with_finals.drop(columns=[Columns.LAST_FINAL_DATE])

    finals = finals.drop(
        columns=[
            Columns.FINAL_PASSED_FLAG,
            Columns.FINAL_FAILED_FLAG,
            Columns.LAST_YEAR_FINAL_GRADE_TEMP,
        ]
    )

    # Right-join onto students so those without final-exam records are retained.
    students_with_finals = students_with_finals.merge(
        enrolled_students[
            [
                Columns.STUDENT_ID,
                Columns.DEGREE,
                Columns.CURRICULUM,
                Columns.ENROLLMENT_DATE,
            ]
        ],
        how="right",
        on=[Columns.STUDENT_ID, Columns.DEGREE, Columns.CURRICULUM],
        suffixes=(".x", ".y"),
    )

    # For students without final exams, use enrollment as the last activity date
    # and fill missing exam indicators with zero.
    _days_since_enrollment = _analysis_date - pd.to_datetime(
        students_with_finals[Columns.ENROLLMENT_DATE]
    )
    students_with_finals[Columns.DAYS_SINCE_LAST_FINAL] = students_with_finals[
        Columns.DAYS_SINCE_LAST_FINAL
    ].fillna(_days_since_enrollment)
    students_with_finals[Columns.CURRICULUM_CHANGE] = students_with_finals[
        Columns.CURRICULUM_CHANGE
    ].fillna(False)
    students_with_finals = students_with_finals.fillna(
        {
            Columns.PASSED_FINALS: 0,
            Columns.FAILED_FINALS: 0,
            Columns.LAST_YEAR_FINAL_GRADE: 0,
        }
    )
    students_with_finals = students_with_finals.drop(columns=[Columns.ENROLLMENT_DATE])

    # Consolidate per-student academic indicators.

    # Combine student, course and final-exam tables.

    # Compute elapsed time since enrollment.
    academic_students = students.copy()
    academic_students[Columns.DAYS_SINCE_ENROLLMENT] = _analysis_date - pd.to_datetime(
        academic_students[Columns.ENROLLMENT_DATE]
    )

    # Retain student identifiers and the elapsed-time indicator.
    academic_students = academic_students[
        [
            Columns.STUDENT_ID,
            Columns.DEGREE,
            Columns.CURRICULUM,
            Columns.DAYS_SINCE_ENROLLMENT,
        ]
    ]

    # Inner-join the prepared student, course and final-exam summaries
    # using the original join keys.
    academic_students = academic_students.merge(
        students_with_courses,
        how="inner",
        on=[Columns.STUDENT_ID, Columns.DEGREE, Columns.CURRICULUM],
        suffixes=(".x", ".y"),
    )
    academic_students = academic_students.merge(
        students_with_finals,
        how="inner",
        on=[Columns.STUDENT_ID, Columns.DEGREE, Columns.CURRICULUM],
        suffixes=(".x", ".y"),
    )

    # Apply the original curriculum-change adjustments and progress formulas.
    # Completed subjects use passed finals; ratios retain the original denominators.
    academic_students[Columns.PASSED_COURSES] = np.where(
        academic_students[Columns.CURRICULUM_CHANGE] == True,
        academic_students[Columns.PASSED_FINALS],
        academic_students[Columns.PASSED_COURSES],
    )
    academic_students[Columns.REGULAR_COURSES] = np.where(
        academic_students[Columns.CURRICULUM_CHANGE] == True,
        academic_students[Columns.PASSED_COURSES],
        academic_students[Columns.REGULAR_COURSES],
    )
    academic_students[Columns.FAILED_COURSES] = np.where(
        academic_students[Columns.CURRICULUM_CHANGE] == True,
        academic_students[Columns.FAILED_FINALS],
        academic_students[Columns.FAILED_COURSES],
    )
    academic_students[Columns.COMPLETED_SUBJECTS] = academic_students[
        Columns.PASSED_FINALS
    ]
    academic_students[Columns.FINAL_COMPLETION_RATIO] = academic_students[
        Columns.COMPLETED_SUBJECTS
    ] / academic_students[Columns.CURRICULUM].map(curriculum_subject_counts)
    academic_students[Columns.COURSE_COMPLETION_RATIO] = np.where(
        academic_students[Columns.CURRICULUM_CHANGE] == True,
        academic_students[Columns.FINAL_COMPLETION_RATIO],
        academic_students[Columns.COURSE_COMPLETION_RATIO],
    )
    academic_students[Columns.FINALS_TO_COURSES_RATIO] = np.where(
        academic_students[Columns.PASSED_COURSES] == 0,
        np.nan,
        academic_students[Columns.COMPLETED_SUBJECTS]
        / academic_students[Columns.PASSED_COURSES],
    )

    # Remove duplicate consolidated student records.
    academic_students = academic_students.drop_duplicates().copy()
    academic_students = academic_students.drop_duplicates(
        subset=[Columns.STUDENT_ID], keep="first"
    ).copy()

    # Analysis population and dropout condition.

    # Retain students whose final-exam completion ratio is at most 50%.
    eligible_students = academic_students[
        academic_students[Columns.FINAL_COMPLETION_RATIO] <= 0.5
    ].copy()

    # Mark dropout after more than 730 days without a final exam and no
    # course activity in 2023, or when administrative status records dropout.
    eligible_students[Columns.DROPPED_OUT] = (
        (eligible_students[Columns.DAYS_SINCE_LAST_FINAL] > pd.Timedelta(days=730))
        & (eligible_students[Columns.LAST_YEAR_SUBJECTS] == 0)
    ) | (eligible_students[Columns.ACADEMIC_STATUS] == AcademicStatus.DROPOUT)

    # Apply the same selection and dropout condition to the core-subject subset.
    students_with_failed_core_subjects = students_with_failed_core_subjects.merge(
        academic_students,
        how="inner",
        on=[
            Columns.STUDENT_ID,
            Columns.CURRICULUM,
            Columns.DEGREE,
            Columns.ENROLLMENT_DATE,
        ],
        suffixes=(".x", ".y"),
    )

    eligible_core_subject_students = students_with_failed_core_subjects.drop(
        columns=[Columns.ENROLLMENT_DATE]
    ).copy()
    eligible_core_subject_students = eligible_core_subject_students[
        eligible_core_subject_students[Columns.FINAL_COMPLETION_RATIO] <= 0.5
    ].copy()
    eligible_core_subject_students[Columns.DROPPED_OUT] = (
        (
            eligible_core_subject_students[Columns.DAYS_SINCE_LAST_FINAL]
            > pd.Timedelta(days=730)
        )
        & (eligible_core_subject_students[Columns.LAST_YEAR_SUBJECTS] == 0)
    ) | (
        eligible_core_subject_students[Columns.ACADEMIC_STATUS_LEFT]
        == AcademicStatus.DROPOUT
    )

    # Select students marked as dropouts.
    dropout_students = eligible_students[
        eligible_students[Columns.DROPPED_OUT] == True
    ].copy()

    # Return the prepared populations to the next stage.
    return {
        "analysis_date": _analysis_date.date().isoformat(),
        "eligible_students": eligible_students,
        "eligible_core_subject_students": eligible_core_subject_students,
        "dropout_students": dropout_students,
    }


if __name__ == "__main__":
    prepare_academic_data()
