"""Source column names and categories with English identifiers.

These constants neither translate nor validate data. Contracts and validation
belong in schemas.py; DataFrames retain their original column names."""

from collections.abc import Mapping
from typing import ClassVar


class Columns:
    """Original academic columns and derived indicators, without renaming them."""

    STUDENT_ID: ClassVar[str] = "id_alumno"
    ACADEMIC_STATUS: ClassVar[str] = "calidad"
    DEGREE: ClassVar[str] = "carrera"
    CURRICULUM: ClassVar[str] = "plan"
    ENROLLMENT_DATE: ClassVar[str] = "fecha_inscripcion"
    BIRTHPLACE: ClassVar[str] = "localidad_nacimiento"
    SUBJECT_CODE: ClassVar[str] = "materia"
    SUBJECT_NAME: ClassVar[str] = "nombre_materia"
    REQUIRED_SUBJECT: ClassVar[str] = "obligatoria"
    RESULT: ClassVar[str] = "resultado"
    COURSE_STATUS: ClassVar[str] = "cond_regularidad"
    GRADE: ClassVar[str] = "nota"
    EXAM_DATE: ClassVar[str] = "fecha"
    COURSE_RECORD_DATE: ClassVar[str] = "fecha_regularidad"
    APPROVAL_METHOD: ClassVar[str] = "forma_aprobacion"
    SUBJECT_COUNT: ClassVar[str] = "cant_materias"
    DAYS_SINCE_ENROLLMENT: ClassVar[str] = "tiempo_desde_ingreso"
    PASSED_COURSES: ClassVar[str] = "cursadas_aprobadas"
    REGULAR_COURSES: ClassVar[str] = "cursadas_regulares"
    PROMOTED_COURSES: ClassVar[str] = "cursadas_promocionadas"
    FAILED_COURSES: ClassVar[str] = "cursadas_desaprobadas"
    LAST_YEAR_COURSE_GRADE: ClassVar[str] = "notas_cursadas_ult_anio"
    LAST_YEAR_SUBJECTS: ClassVar[str] = "materias_anotado_ult_anio"
    COURSE_COMPLETION_RATIO: ClassVar[str] = "porc_cursadas"
    PASSED_FINALS: ClassVar[str] = "finales_aprobados"
    FAILED_FINALS: ClassVar[str] = "finales_desaprobados"
    LAST_YEAR_FINAL_GRADE: ClassVar[str] = "nota_finales_ult_anio"
    DAYS_SINCE_LAST_FINAL: ClassVar[str] = "dias_dsd_ultimo_final"
    FINAL_COMPLETION_RATIO: ClassVar[str] = "porc_finales"
    DROPPED_OUT: ClassVar[str] = "deserto"
    CURRICULUM_CHANGE: ClassVar[str] = "cambio_plan"
    COMPLETED_SUBJECTS: ClassVar[str] = "total_materias_finalizadas"
    FINALS_TO_COURSES_RATIO: ClassVar[str] = "relacion_finales_cursadas"
    COURSE_PASSED_FLAG: ClassVar[str] = "_cursada_aprobada"
    COURSE_REGULAR_FLAG: ClassVar[str] = "_cursada_regular"
    COURSE_PROMOTED_FLAG: ClassVar[str] = "_cursada_promocionada"
    COURSE_FAILED_FLAG: ClassVar[str] = "_cursada_desaprobada"
    LAST_YEAR_COURSE_GRADE_TEMP: ClassVar[str] = "_nota_cursada_ult_anio"
    LAST_YEAR_SUBJECT_TEMP: ClassVar[str] = "_materia_anotada_ult_anio"
    FINAL_PASSED_FLAG: ClassVar[str] = "_final_aprobado"
    FINAL_FAILED_FLAG: ClassVar[str] = "_final_desaprobado"
    LAST_YEAR_FINAL_GRADE_TEMP: ClassVar[str] = "_nota_final_ult_anio"
    LAST_FINAL_DATE: ClassVar[str] = "_fecha_ultimo_final"
    GROUP: ClassVar[str] = "grupo"
    COUNT: ClassVar[str] = "cantidad"
    HIERARCHICAL_GROUP: ClassVar[str] = "grupo_jerarquico"
    KMEANS_GROUP: ClassVar[str] = "grupo_kmeans"
    ACADEMIC_STATUS_LEFT: ClassVar[str] = "calidad.x"


class AcademicStatus:
    """Administrative status values recorded by SIU."""

    DROPOUT: ClassVar[str] = "Abandono"
    GRADUATED: ClassVar[str] = "Egreso"


class CourseStatus:
    """Recorded course completion conditions."""

    REGULAR: ClassVar[str] = "Regular"
    PROMOTED: ClassVar[str] = "Promocionó"


class ApprovalMethod:
    """Approval methods recorded in the source data."""

    EQUIVALENCE: ClassVar[str] = "Equivalencia"


class ResultCode:
    """Source result codes."""

    PASSED: ClassVar[str] = "A"
    FAILED: ClassVar[str] = "R"
    ABSENT: ClassVar[str] = "U"


class RequiredSubject:
    """Curriculum requirement codes."""

    YES: ClassVar[str] = "S"


class CoreSubjects:
    """Core subjects used by the original processing pipeline."""

    INTRO_PROGRAMMING_I: ClassVar[str] = "Introducción a la Programación I"
    INTRO_PROGRAMMING_II: ClassVar[str] = "Introducción a la Programación II"
    ALGORITHMS_I: ClassVar[str] = "Análisis y Diseño de Algoritmos I"
    ALGORITHMS_II: ClassVar[str] = "Análisis y Diseño de Algoritmos II"
    OBJECT_ORIENTED_PROGRAMMING: ClassVar[str] = "Programación Orientada a Objetos"


# Preserve documented report CSV column names. Internal result keys
# use English; these aliases apply only during export.
CSV_REPORT_COLUMNS: Mapping[str, str] = {
    "seed": "semilla",
    "seeds": "semillas",
    "inertia": "inercia",
    "ari_hierarchical": "ari_jerarquico",
    "ari_kmeans_reference": "ari_referencia_kmeans",
    "smallest_group": "grupo_menor",
    "largest_group": "grupo_mayor",
    "negative_pct": "negativos_pct",
    "iterations": "iteraciones",
    "iteration_limit_reached": "limite_iteraciones",
    "ari_min": "ari_minimo",
    "ari_median": "ari_mediano",
    "ari_max": "ari_maximo",
    "inertia_min": "inercia_minima",
    "inertia_max": "inercia_maxima",
    "silhouette_min": "silhouette_minimo",
    "silhouette_max": "silhouette_maximo",
}
