# Student clustering comparison

Operations Research final project — Faculty of Exact Sciences, UNICEN.

The project compares how **the same students are grouped by hierarchical clustering, K-Means and DBSCAN using the original academic features**. It examines group sizes, membership and academic profiles to identify preserved, split or merged groups and students classified as noise. Hierarchical labels are a comparison reference, not ground truth, and are never K-Means or DBSCAN input features.

## Current reference

The fixed analysis date is `2026-10-01`. The input contains 2,587 students and ten original features, including the dropout indicator.

| Method | Reference settings | Groups | Noise | Silhouette |
|---|---|---:|---:|---:|
| Hierarchical | Euclidean distance, Ward, height 35 | 7 | 0 | 0.295444 |
| K-Means | k=7, 25 initializations, seed 123 | 7 | 0 | 0.365474 |
| DBSCAN | eps=1.5, min_samples=5 | 1 | 194 (7.5%) | Unavailable: one non-noise group |

The hierarchical R-to-Python migration was verified for five analysis dates. Reproducing the exact publication date or its reported numbers is outside the project scope. DBSCAN exploration is complete without adopting it as the selected segmentation. K-Means experiments retain all original features and investigate parameter and initialization sensitivity. See the [research documentation](docs/README.md) and [K-Means experiment record](docs/resultados/experiencia-kmeans.md).

## Setup and commands

Use Python 3.11 and uv. Original CSV files must be available locally under `data/`:

- `001_alumnos.csv`
- `002_regularidades.csv`
- `003_historia_academica.csv`
- `000_materias_planes.csv`

```bash
uv sync
uv run python main.py --date 2026-10-01 --output output
```

`--date` takes precedence over `ANALYSIS_DATE`, then defaults to `2026-10-01`. The original last-year activity indicator still refers to 2023; changing the analysis date does not shift that window.

The main pipeline runs all three reference methods and the five fixed DBSCAN cases. To change the individual DBSCAN fit:

```bash
uv run python main.py --eps 0.8 --min-samples 10 --output output/local-comparison
```

These settings are exploratory. `min_samples` includes the observation itself; the fixed cases retain their own settings.

## Independent K-Means experiments

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 uv run python -m src.runs.kmeans_experiments --date 2026-10-01 --output output/k-means/exploration
```

The protocol tests k=5 through 9, 100 initializations and thirty fixed seeds: 123 and 0 through 28. If the minimum pairwise ARI for a k is below 0.95, it repeats those seeds with 200 initializations. The threshold controls repetition, not acceptance. Thread limits make runtime more predictable without changing the academic protocol.

For a smaller explicit experiment:

```bash
uv run python -m src.runs.kmeans_experiments --k 6 7 --seeds 123 0 1 --n-init 100 --n-init-control 200 --output output/k-means/local-experiment
```

Each k/n_init exports its lowest-inertia representative, breaking ties by declared seed order. No configuration is automatically selected as the academic winner. The main pipeline continues to use its original k=7/n_init=25/seed=123 reference.

Experiment outputs include `protocol.json`, `metrics.csv`, `stability.csv`, `seed_pairs.csv` and `all_assignments.csv`. Each representative directory contains assignments, means, distributions, quartiles, standardized centers, Silhouette diagnostics, intersection profiles, correspondence tables, fragmentation and merge tables, and profile persistence across seeds. Figures include `plots/correspondence.png`, with membership counts and percentages normalized within each hierarchical row.

Pairwise ARI measures overall initialization sensitivity. Group matching maximizes overlap before measuring retention and Jaccard; this avoids treating label numbers as identities. These experiments do not measure stability against changes in sample composition.

## English code and original data names

Identifiers, comments, docstrings, errors, CLI options, plot labels and generated output paths use English. Original CSV names, column names and categorical values remain unchanged so the original data can still be read and filtered correctly.

`src/data/constants.py` provides class attributes with English identifiers and original values:

```python
from src.data.constants import AcademicStatus, Columns

dropouts = students[
    students[Columns.ACADEMIC_STATUS] == AcademicStatus.DROPOUT
]
# Columns.ACADEMIC_STATUS refers to the original status column.
# AcademicStatus.DROPOUT contains the original administrative category.
```

`ClassVar[str]` marks these as class attributes. Uppercase names identify constants by convention; Python does not enforce runtime immutability. `Columns.DROPPED_OUT` identifies the computed dropout indicator, which is distinct from the administrative status category.

`src/data/schemas.py` defines the contracts and Pandera validation. English field identifiers use aliases to retain the original DataFrame column names, order, types and validation rules. Report CSV column names also retain their documented values through `CSV_REPORT_COLUMNS`. Original reference documents and historical research artifacts retain their original language and filenames.

The Python API uses English names:

```python
from src.data.preparation import prepare_input
from src.methods.kmeans import analyze
from main import main

entry = prepare_input(analysis_date="2026-10-01")
result = analyze(entry["matrix"], entry["original_values"])
comparison = main(date="2026-10-01", output="output")
```

`ClusteringInput` contains `original_values`, `matrix`, `student_ids` and `analysis_date`. Matrices use sample standardization (`ddof=1`); identifiers and cluster labels are excluded. The original dropout feature is always retained, so group dropout proportions describe membership and do not independently validate dropout prediction.

Method results include `labels`, `summary`, `silhouette`, `silhouette_mean`, `silhouette_population`, `silhouette_reason` and `parameters`, with method-specific diagnostics such as centers/inertia, linkage or neighbor distances. `main()` returns `entry`, `results` (with `hierarchical`, `kmeans`, `dbscan`) and `dbscan_cases`. Runs expose `run_cases(entry, directory)` and return `result` and `cases`.

## Output layout

```text
output/
├── hierarchical/
│   ├── cluster_summary.csv
│   └── plots/                    # PNG; PDF for internal dendrograms and zooms
├── k-means/
│   ├── plots/                    # Reference PNG figures
│   └── exploration/              # Explicit independent experiments
│       ├── reference/
│       ├── k<k>_n<n_init>/
│       └── protocol.json
└── dbscan/
    ├── plots/                    # Includes neighbors.png
    └── experiments/
        ├── <case>/plots/
        └── plots/comparison.png
```

`data/*.csv` and generated `output/` artifacts are ignored by Git because they contain original records and student identifiers. Aggregate figures needed for research deliverables are retained alongside the relevant documents.

## Source organization

```text
main.py                           # CLI for src.runs.comparison
src/
├── data/
│   ├── constants.py              # Original names and categories
│   ├── schemas.py                # Pandera and TypedDict contracts
│   ├── processing.py             # CSV loading, filters and indicators
│   └── preparation.py            # Identity, feature selection, standardization
├── methods/
│   ├── schemas.py                # Typed result contracts
│   ├── hierarchical.py
│   ├── kmeans.py
│   ├── dbscan.py
│   └── lasso.py
└── runs/
    ├── comparison.py             # Common input and method coordination
    ├── hierarchical.py
    ├── kmeans.py                 # Reference run
    ├── kmeans_experiments.py      # Explicit parameter/seed experiments
    ├── dbscan.py                  # Individual fit and fixed cases
    ├── lasso.py                   # Independent supervised baseline
    ├── schemas.py
    ├── _reporting.py
    └── visualization/
        ├── outputs.py            # Plot bundles and output selection
        ├── saving.py             # Export and close figures
        ├── schemas.py
        ├── correspondence.py
        ├── bars.py
        ├── profiles.py
        ├── silhouette.py
        ├── lines.py
        ├── dendrograms.py
        └── scatter.py
```

Plot functions return `Figure` objects. `save_figure` saves and closes them; output builders return `None`. Internal dendrograms and first-50-observation zooms are diagnostics and do not change the reference assignment. The hierarchical Silhouette curve for k=2 through 15 does not alter the fixed height-35 cut.

LASSO is a separate baseline; its coefficients do not select or weight clustering features:

```bash
ANALYSIS_DATE=2026-10-01 uv run --group antecedentes python -m src.runs.lasso
```

Original R scripts and migration notebooks remain under `Legacy/`.

## Verification

```bash
uv run ruff check main.py src tests
uv run pytest -q
```

Language refactoring must preserve original feature values, row identities, cluster membership and numerical diagnostics.
