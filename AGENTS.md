# Repository guidelines

## Study features

- Always retain the original features in clustering inputs, including `deserto`. Compare changes in grouping using the same academic input as the original study.
- Explore method parameters while retaining these features, their preparation and the common standardization. Do not propose removing variables from the K-Means protocol.
- Historical DBSCAN tests without `deserto` were exceptional diagnostics; they do not establish a feature-selection policy for this project.

## Correspondence plots and the final report

- Include the hierarchical/K-Means correspondence heatmap in the final report. The user prefers this format for explaining group preservation, fragmentation and merging.
- Use hierarchical groups as rows and K-Means groups as columns. Show the student count and percentage within the hierarchical row in each cell. Include row sizes and explain the percentage denominator.
- Encode percentages through color intensity with an explicit scale and legend. State that method labels are independent and record the analysis date and K-Means settings.
- The original visual reference is `output/k-means/diagnostico-2026-10-11/correspondencias.png`, shown in `lectura.md` in that folder. These historical generated files are ignored by Git. Regenerate the plot using the documented final settings and keep it with the deliverables. Current runs export the English filename `plots/correspondence.png`.

## Python typing

- Annotate parameters and return values of new or modified functions. Apply typing incrementally in the modules being changed.
- Use concrete types when known: `matplotlib.figure.Figure` for figures, `pd.DataFrame` and `pd.Series` for tables and series, `str | Path` for paths and `None` for functions without a return value.
- Functions named `plot_*` must return `Figure`. `save_figure` accepts a `Figure` and returns `None`; output-bundle builders also return `None`.
- Reuse existing contracts such as `ClusteringInput`. For dictionaries with a known structure, prefer `TypedDict` with explicit fields and `NotRequired` for optional fields over unparameterized dictionaries or `Any`.
- Use `ArrayLike` for numerical inputs accepting lists, arrays or series, and `NDArray` when the contract requires a NumPy array. Use `Sequence` or `Mapping` for read-only collections.
- Annotations document contracts and help the editor; they do not replace required runtime checks or Pandera data validation.

## Language and file names

- Write all active code in English, including identifiers, comments, docstrings, schema descriptions, errors, console messages, CLI options, plot labels and output paths.
- Preserve original column names and source-data literals required to read and filter the original CSV files. These include administrative categories and subject names. Do not translate the underlying data or change the analysis to satisfy a language convention.
- Centralize source column names and categories in `src/data/constants.py`. Use English identifiers whose values match the original data. Separate columns (`Columns`) from categories (`AcademicStatus`, `CourseStatus`, etc.). Use `ClassVar[str]` for the class attributes; uppercase names document the constant convention without enforcing runtime immutability.
- Use `schemas.py` for structural contracts defined with `TypedDict` and Pandera. Document whether a contract validates data at runtime or provides typing only.
- Keep constants separate from schemas: constants identify names and codes; schemas define contracts and validate data. Use Pandera aliases when an English schema attribute refers to an original column name.
- Technical documentation and repository instructions are in English. Preserve original reference documents and historical research artifacts in their original language.

## Verification

- After Python changes, run `uv run ruff check main.py src tests` and the relevant tests with `uv run pytest -q`. If `.venv` is ready, its executables may be used directly.
