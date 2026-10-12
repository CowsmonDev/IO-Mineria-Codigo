# Project documentation

Main question: **how does grouping the same students change when K-Means and DBSCAN use the same academic input as the hierarchical reference?**

The primary output is each student's group assignment. Sizes, academic profiles and separation follow from those assignments. DBSCAN may classify students as noise. Interpretation relates preserved, split and merged groups to profiles described in the original study.

## Reading guide

| Document | Purpose |
|---|---|
| [Study criteria](criterios-del-trabajo.md) | Goals, scope, comparison criteria and accepted R-to-Python equivalence. |
| [Report draft](referencias/informe.md) | Academic background, input, methods and comparison questions. |
| [File-level flow](flujos/flujo-archivos.md) | Current preparation, method runs and output responsibilities. |
| [Final DBSCAN report](resultados/experiencia-dbscan.pdf) | Five cases, interpretation and decision not to adopt DBSCAN as the selected segmentation. |
| [Editable report source](resultados/experiencia-dbscan.docx) | Word version of the main DBSCAN document. |
| [DBSCAN technical annex](resultados/anexo-tecnico-dbscan.md) | Protocols, experiments, concordance, sensitivity and historical diagnostics. |
| [K-Means experiment record](resultados/experiencia-kmeans.md) | Original features, initialization sensitivity, fragmentation and profiles. |
| [R-to-Python verification](resultados/verificacion-fechas-r-python.md) | Completed validation of students, features and clustering on five dates. |

DBSCAN evaluation is complete for the studied protocol. Its final report is the conclusion reference, while the annex retains supporting evidence. Historical searches are not part of `main.py`. K-Means exploration runs separately with `python -m src.runs.kmeans_experiments`; the linked record explains its results. The [historical K-Means annex](referencias/informe.md#anexo-histórico-de-k-means) remains in the report draft.

## Original references

- [Clementi and Salias report](referencias/IO-Mineria-Informe-Clementi-Salias.pdf): section 4.3, cluster profiles; section 5, conclusions and future work.
- [English article](<referencias/Analyzing students dropout using penalized logistic regression and hierarchical clustering a case study in systems engineering.docx.pdf>): section 4.4, profiles; section 5, future work.
- [R scripts](../Legacy/scripts): original preparation, LASSO and clustering.

Original documents and historical academic records retain their original language. The working analysis date is `2026-10-01`. R-to-Python equivalence is verified; reconstructing the publication date and figures is outside the project scope.

The current code, CLI and generated paths use English. The original source data and report CSV columns retain their names. The [main README](../README.md) documents current installation, commands and Python interfaces. Historical output directories remain available with their original names.
