"""Shared synthetic input for tests."""

import numpy as np
import pandas as pd
import pytest

from src.data.constants import Columns
from src.data.preparation import standardize
from src.data.schemas import ClusteringInput


@pytest.fixture
def entry() -> ClusteringInput:
    rng = np.random.default_rng(22)
    groups = np.repeat(np.arange(1, 8), 10)
    original_values = pd.DataFrame(
        {
            Columns.DAYS_SINCE_ENROLLMENT: groups * 100 + rng.normal(0, 2, len(groups)),
            Columns.PASSED_COURSES: groups.astype(float) * 3,
            Columns.PROMOTED_COURSES: groups.astype(float),
            Columns.FAILED_COURSES: (groups % 3).astype(float),
            Columns.LAST_YEAR_SUBJECTS: (groups % 4).astype(float),
            Columns.PASSED_FINALS: groups * 10 + rng.normal(0, 0.2, len(groups)),
            Columns.FAILED_FINALS: (groups % 2).astype(float),
            Columns.DAYS_SINCE_LAST_FINAL: groups.astype(float) * 20,
            Columns.FINAL_COMPLETION_RATIO: groups / 20,
            Columns.DROPPED_OUT: (groups > 4).astype(float),
        }
    )
    return {
        "original_values": original_values,
        "matrix": standardize(original_values),
        "student_ids": np.arange(200, 270),
        "analysis_date": "2026-10-01",
    }
