"""Run the hierarchical reference and generate its outputs."""

from pathlib import Path

from src.data.constants import Columns
from src.data.schemas import ClusteringInput
from src.methods import hierarchical
from src.methods.schemas import ClusteringResult
from src.runs._reporting import print_result
from src.runs.schemas import ClusteringRun
from src.runs.visualization.outputs import generate_method_plots


def run_cases(
    entry: ClusteringInput, directory: str | Path
) -> ClusteringRun[ClusteringResult]:
    """Run the fixed reference on the common input and save outputs."""
    result = hierarchical.analyze(entry["matrix"], entry["original_values"])
    directory = Path(directory)
    generate_method_plots(entry, {"hierarchical": result}, directory)
    save_summary(result, directory / "hierarchical")
    print_result("hierarchical", result)
    return {
        "result": result,
        "cases": [
            {
                "name": "reference",
                "description": "Ward reference h=35",
                "result": result,
            }
        ],
    }


def save_summary(result: ClusteringResult, directory: str | Path) -> None:
    """Export the hierarchical summary using the original R column names."""
    columns = {
        Columns.COUNT: "cantidad_observaciones",
        Columns.PASSED_COURSES: "media_cursadas_aprobadas",
        Columns.FAILED_COURSES: "media_cursadas_desaprobadas",
        Columns.LAST_YEAR_SUBJECTS: "media_materias_anotado_ult_anio",
        Columns.PASSED_FINALS: "media_finales_aprobados",
        Columns.FAILED_FINALS: "media_finales_desaprobados",
        Columns.PROMOTED_COURSES: "media_cursadas_promocionadas",
        Columns.FINAL_COMPLETION_RATIO: "media_porc_finales",
        Columns.DAYS_SINCE_ENROLLMENT: "media_T_desde_ingreso",
        Columns.DROPPED_OUT: "media_deserto",
        Columns.DAYS_SINCE_LAST_FINAL: "media_dias_dsd_ultimo_final",
    }
    # Also support synthetic test inputs.
    summary = result["summary"]
    available_columns = [col for col in columns if col in summary]
    table = (
        summary[available_columns]
        .rename(columns=columns)
        .rename_axis("cluster")
        .reset_index()
    )
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    table.to_csv(directory / "cluster_summary.csv", index=False)
