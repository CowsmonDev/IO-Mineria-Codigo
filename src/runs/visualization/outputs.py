"""Assemble plots, titles and output paths for each run."""

from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np

from src.data.constants import Columns
from src.data.schemas import ClusteringInput

from .bars import plot_bar_comparison, plot_bars
from .dendrograms import plot_dendrogram, plot_internal_dendrogram
from .lines import plot_lines
from .profiles import plot_profile
from .saving import save_figure
from .scatter import plot_dropout_by_group, plot_progress_vs_promoted_courses
from .schemas import PlotCase, PlotResult
from .silhouette import plot_silhouette

FOLDERS = {"hierarchical": "hierarchical", "kmeans": "k-means", "dbscan": "dbscan"}
TITLES = {"hierarchical": "Hierarchical", "kmeans": "K-Means", "dbscan": "DBSCAN"}


def generate_run_plots(
    entry: ClusteringInput,
    result: PlotResult,
    title: str,
    folder: str | Path,
    *,
    horizontal: bool = False,
) -> None:
    """Build common plots for one configuration and neighbor diagnostics, if present."""
    folder = Path(folder)
    summary = result["summary"]
    labels = ["Noise" if group == -1 else str(group) for group in summary.index]
    figure = plot_bars(
        labels,
        summary[Columns.COUNT],
        title=f"{title}: group sizes",
        xlabel="Group",
        ylabel="Students",
    )
    save_figure(figure, folder / "sizes")
    figure = plot_silhouette(
        result["silhouette"],
        result["labels"],
        title=title,
        reason=result["silhouette_reason"],
    )
    save_figure(figure, folder / "silhouette")

    original_values = entry["original_values"]
    for variable in (Columns.PASSED_FINALS, Columns.PROMOTED_COURSES):
        if variable in original_values:
            figure = plot_profile(
                original_values,
                result["labels"],
                variable,
                title=f"{title}: {variable}",
                horizontal=horizontal,
            )
            save_figure(figure, folder / f"profile_{variable}")
    if Columns.DROPPED_OUT in original_values:
        figure = plot_bars(
            labels,
            summary[Columns.DROPPED_OUT],
            title=f"{title}: dropout by group\n(feature included in the input)",
            xlabel="Group",
            ylabel="Dropout proportion",
            ylim=(0, 1),
        )
        save_figure(figure, folder / "dropout_profile")

    if "neighbor_distances" in result:
        m = result["parameters"]["min_samples"]
        eps = result["parameters"]["eps"]
        distances = result["neighbor_distances"]
        figure = plot_lines(
            np.arange(1, len(distances) + 1),
            distances,
            title=f"DBSCAN: min_samples={m} (includes self)",
            xlabel="Ordered observation",
            ylabel=f"Distance to neighbor {m - 1} excluding self",
            reference=eps,
            reference_label=f"eps={eps}",
        )
        save_figure(figure, folder / "neighbors")


def generate_hierarchical_diagnostics(
    entry: ClusteringInput,
    result: PlotResult,
    folder: str | Path,
) -> None:
    """Add diagnostics specific to the hierarchical reference."""
    folder = Path(folder)
    height = result["parameters"]["height"]
    figure = plot_dendrogram(
        result["linkage_matrix"],
        title=f"Hierarchical: Ward, cut height {height}",
        cut_height=height,
        ylim=(0, 50),
    )
    save_figure(figure, folder / "overall_dendrogram")
    curve = result["silhouette_by_k"]
    figure = plot_lines(
        curve.index,
        curve.values,
        title="Hierarchical: Silhouette for k=2 to 15",
        xlabel="Number of groups (k)",
        ylabel="Mean Silhouette",
        marker="o",
        size=(8, 5),
    )
    save_figure(figure, folder / "silhouette_by_k")

    # Subgroups and zooms are diagnostics; they do not change reference groups.
    for group in np.unique(result["labels"]):
        data = entry["matrix"].iloc[np.flatnonzero(result["labels"] == group)]
        if len(data) < 3:
            continue
        figure = plot_internal_dendrogram(
            data,
            title=f"Internal dendrogram - Cluster {group}",
            subgroups=4,
        )
        save_figure(
            figure, folder / f"cluster_dendrogram_{group}", formats=("png", "pdf")
        )
        if len(data) >= 500:
            figure = plot_internal_dendrogram(
                data.iloc[:50],
                title=f"Zoom - Cluster {group} (first 50 observations)",
                subgroups=3,
                size=(12, 8),
                labels=True,
            )
            save_figure(
                figure,
                folder / f"cluster_zoom_dendrogram_{group}",
                formats=("png", "pdf"),
            )

    original_values = entry["original_values"]
    rng = np.random.default_rng(1)
    if Columns.DROPPED_OUT in original_values:
        figure = plot_dropout_by_group(
            original_values[Columns.DROPPED_OUT],
            result["labels"],
            title="Dropout distribution by cluster",
            rng=rng,
        )
        save_figure(figure, folder / "dropout_distribution")
    if {
        Columns.PROMOTED_COURSES,
        Columns.FINAL_COMPLETION_RATIO,
        Columns.DROPPED_OUT,
    }.issubset(original_values.columns):
        figure = plot_progress_vs_promoted_courses(
            original_values,
            title="Dropout by promoted courses and degree progress",
            rng=rng,
        )
        save_figure(figure, folder / "progress_vs_promoted_courses")


def generate_method_plots(
    entry: ClusteringInput,
    results: Mapping[str, PlotResult],
    directory: str | Path,
) -> None:
    """Export per-method plot sets under <directory>/<method>/plots/."""
    for method, result in results.items():
        folder = Path(directory) / FOLDERS[method] / "plots"
        generate_run_plots(
            entry,
            result,
            TITLES[method],
            folder,
            horizontal=method == "hierarchical",
        )
        if method == "hierarchical":
            generate_hierarchical_diagnostics(entry, result, folder)


def generate_dbscan_experiment_plots(
    entry: ClusteringInput,
    run_cases: Sequence[PlotCase],
    directory: str | Path,
) -> None:
    """Save fixed DBSCAN cases and their joint metric comparison."""
    root = Path(directory) / "dbscan" / "experiments"
    for case in run_cases:
        generate_run_plots(
            entry,
            case["result"],
            f"DBSCAN: {case['description']}",
            root / case["name"] / "plots",
        )

    names = [case["name"] for case in run_cases]
    results = [case["result"] for case in run_cases]
    noise = [100 * r["noise"] / len(entry["matrix"]) for r in results]
    largest_groups = []
    for result in results:
        sizes = result["summary"].drop(index=-1, errors="ignore")[Columns.COUNT]
        largest_groups.append(100 * sizes.max() / sizes.sum() if len(sizes) else np.nan)
    figure = plot_bar_comparison(
        names,
        [
            ("Number of groups (excluding noise)", [r["n_groups"] for r in results]),
            ("Noise (% of all students)", noise),
            ("Largest group (% of clustered students)", largest_groups),
        ],
        title=f"DBSCAN: casos fijos over la misma entrada ({entry['analysis_date']})",
    )
    save_figure(figure, root / "plots" / "comparison")
