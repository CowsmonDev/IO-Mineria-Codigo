"""Reproducible K-Means experiments retaining all ten original features.

Run with python -m src.runs.kmeans_experiments. The main pipeline retains
k=7, n_init=25 and seed 123 as its reference; this exploration is independent."""

import argparse
import json
from collections.abc import Sequence
from hashlib import sha256
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import adjusted_rand_score

from src.data.constants import CSV_REPORT_COLUMNS, Columns
from src.data.preparation import prepare_input, validate_input
from src.data.schemas import ClusteringInput
from src.methods import hierarchical, kmeans
from src.methods.schemas import KMeansResult
from src.runs.schemas import (
    KMeansCase,
    KMeansExploration,
    KMeansMetric,
    KMeansStability,
)
from src.runs.visualization.correspondence import plot_correspondence
from src.runs.visualization.outputs import generate_run_plots
from src.runs.visualization.saving import save_figure
from src.runs.visualization.schemas import PlotResult

K_VALUES = (5, 6, 7, 8, 9)
SEEDS = (123, *range(29))


def compare_profiles(
    reference: NDArray[np.integer],
    labels: NDArray[np.integer],
) -> pd.DataFrame:
    """Match groups by maximum overlap, independently of label numbers.

    Jaccard is intersection over union; retention is the fraction of reference
    members retained. Matching is one-to-one for equal group counts and does
    not define ground-truth classes."""
    if reference.ndim != 1 or labels.ndim != 1 or len(reference) != len(labels):
        raise ValueError("Labels must be vectors aligned by student.")
    table = pd.crosstab(reference, labels)
    if table.empty or table.shape[0] != table.shape[1]:
        raise ValueError("The same number of nonempty groups is required.")
    rows, columns = linear_sum_assignment(-table.to_numpy())
    records = []
    for i, j in zip(rows, columns):
        intersection = int(table.iloc[i, j])
        count = int(table.iloc[i].sum())
        destination = int(table.iloc[:, j].sum())
        records.append(
            (
                table.index[i],
                table.columns[j],
                count,
                destination,
                intersection / count,
                intersection / (count + destination - intersection),
            )
        )
    return pd.DataFrame(
        records,
        columns=[
            "grupo_representante",
            "grupo_semilla",
            "cantidad_representante",
            "cantidad_semilla",
            "retencion",
            "jaccard",
        ],
    )


def save_case(
    entry: ClusteringInput,
    result: KMeansResult,
    hierarchical_labels: NDArray[np.integer],
    folder: Path,
) -> None:
    """Export assignments, profiles and evidence of fragmentation and merging."""
    folder.mkdir(parents=True, exist_ok=True)
    labels = result["labels"]
    pd.DataFrame(
        {
            Columns.STUDENT_ID: entry["student_ids"],
            Columns.HIERARCHICAL_GROUP: hierarchical_labels,
            Columns.KMEANS_GROUP: labels,
            "silhouette": result["silhouette"],
        }
    ).to_csv(folder / "assignments.csv", index=False)
    result["summary"].to_csv(folder / "means.csv")
    grouped = (
        entry["original_values"]
        .assign(**{Columns.GROUP: labels})
        .groupby(Columns.GROUP)
    )
    grouped.agg(["median", "std", "min", "max"]).to_csv(folder / "distributions.csv")
    grouped.quantile([0.25, 0.75]).to_csv(folder / "quartiles.csv")
    intersections = (
        entry["original_values"]
        .assign(
            **{
                Columns.HIERARCHICAL_GROUP: hierarchical_labels,
                Columns.KMEANS_GROUP: labels,
            },
        )
        .groupby([Columns.HIERARCHICAL_GROUP, Columns.KMEANS_GROUP])
    )
    intersection_means = intersections.mean()
    intersection_means.insert(0, Columns.COUNT, intersections.size())
    intersection_means.to_csv(folder / "intersecciones_means.csv")
    intersections.median().to_csv(folder / "intersection_medians.csv")
    pd.DataFrame(
        result["centers"],
        columns=entry["matrix"].columns,
        index=pd.Index(range(1, len(result["centers"]) + 1), name=Columns.GROUP),
    ).to_csv(folder / "standardized_centers.csv")
    sil = (
        pd.DataFrame(
            {
                Columns.GROUP: labels,
                "silhouette": result["silhouette"],
                "negativo": result["silhouette"] < 0,
            }
        )
        .groupby(Columns.GROUP)
        .agg(
            silhouette_media=("silhouette", "mean"),
            silhouette_mediana=("silhouette", "median"),
            negativos_fraccion=("negativo", "mean"),
        )
    )
    sil.to_csv(folder / "silhouette_by_group.csv")
    cross_table = pd.crosstab(
        pd.Series(hierarchical_labels, name="jerarquico"),
        pd.Series(labels, name="kmeans"),
    )
    cross_table.to_csv(folder / "correspondence.csv")
    by_row = cross_table.div(cross_table.sum(axis=1), axis=0)
    by_column = cross_table.div(cross_table.sum(axis=0), axis=1)
    by_row.to_csv(folder / "proportions_by_hierarchical.csv")
    by_column.to_csv(folder / "proportions_by_kmeans.csv")
    pd.DataFrame(
        {
            Columns.COUNT: cross_table.sum(axis=1),
            "destinos": (cross_table > 0).sum(axis=1),
            "destino_principal": cross_table.idxmax(axis=1),
            "fraccion_destino_principal": by_row.max(axis=1),
            "destinos_efectivos": 1 / by_row.pow(2).sum(axis=1),
        }
    ).to_csv(folder / "fragmentation.csv")
    pd.DataFrame(
        {
            Columns.COUNT: cross_table.sum(axis=0),
            "origenes": (cross_table > 0).sum(axis=0),
            "origen_principal": cross_table.idxmax(axis=0),
            "fraccion_origen_principal": by_column.max(axis=0),
        }
    ).to_csv(folder / "merges.csv")
    parameters = result["parameters"]
    title = (
        f"K-Means k={parameters['n_clusters']}, n_init={parameters['n_init']}, "
        f"seed={parameters['random_state']}"
    )
    # The plotting contract consumes only common fields. Full K-Means settings
    # are already included in each plot title.
    plot_result: PlotResult = {
        "labels": result["labels"],
        "summary": result["summary"],
        "silhouette": result["silhouette"],
        "silhouette_reason": result["silhouette_reason"],
        "parameters": {},
    }
    generate_run_plots(entry, plot_result, title, folder / "plots")
    save_figure(
        plot_correspondence(
            cross_table,
            title=f"{title}\n{len(labels)} students · date {entry['analysis_date']}",
        ),
        folder / "plots" / "correspondence",
    )


def explore(
    entry: ClusteringInput,
    directory: str | Path,
    *,
    k_values: Sequence[int] = K_VALUES,
    seeds: Sequence[int] = SEEDS,
    n_init: int = 100,
    n_init_control: int = 200,
    control_threshold: float = 0.95,
) -> KMeansExploration:
    """Explore seeds and k without selecting a winner or changing features.

    Repeat with more initializations when the minimum pairwise ARI falls below
    the fixed threshold. The threshold controls repetition, not acceptance.
    For each k/n_init, export the lowest-inertia fit, breaking ties by seed order;
    Silhouette and agreement with the hierarchical reference do not select it."""
    validate_input(entry)
    if not k_values or len(set(k_values)) != len(k_values):
        raise ValueError("Require distinct values of k.")
    if len(seeds) < 2 or len(set(seeds)) != len(seeds):
        raise ValueError("Require at least two distinct seeds.")
    if any(not isinstance(s, int) or isinstance(s, bool) or s < 0 for s in seeds):
        raise ValueError("Seeds must be nonnegative integers.")
    if any(
        not isinstance(k, int)
        or isinstance(k, bool)
        or not 2 <= k < len(entry["matrix"])
        for k in k_values
    ):
        raise ValueError("Each k must satisfy 2 <= k < number of students.")
    if not isinstance(n_init, int) or isinstance(n_init, bool) or n_init < 1:
        raise ValueError("n_init must be a positive integer.")
    if (
        not isinstance(n_init_control, int)
        or isinstance(n_init_control, bool)
        or n_init_control <= n_init
        or not 0 <= control_threshold <= 1
    ):
        raise ValueError(
            "The control requires more initializations and a threshold between 0 and 1."
        )
    x = entry["matrix"].to_numpy(dtype=float)
    if len(np.unique(x, axis=0)) < max(k_values):
        raise ValueError("Not enough distinct observations for all requested k values.")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    distances = squareform(pdist(x))
    hierarchical_reference = hierarchical.analyze(x, entry["original_values"])
    kmeans_reference = kmeans.analyze(
        x,
        entry["original_values"],
        silhouette_distances=distances,
    )
    save_case(
        entry,
        kmeans_reference,
        hierarchical_reference["labels"],
        directory / "reference",
    )
    metrics: list[KMeansMetric] = []
    stability: list[KMeansStability] = []
    pairs: list[tuple[int, int, int, int, float]] = []
    representatives: list[KMeansCase] = []
    assignments: dict[str, ArrayLike] = {Columns.STUDENT_ID: entry["student_ids"]}
    assignments["jerarquico"] = hierarchical_reference["labels"]
    assignments["kmeans_referencia"] = kmeans_reference["labels"]

    def batch(k: int, initializations: int) -> float:
        results: list[KMeansResult] = []
        for seed in seeds:
            result = kmeans.analyze(
                x,
                entry["original_values"],
                n_clusters=k,
                n_init=initializations,
                random_state=seed,
                silhouette_distances=distances,
            )
            results.append(result)
            labels = result["labels"]
            assignments[f"k{k}_n{initializations}_s{seed}"] = labels
            sizes = result["summary"][Columns.COUNT]
            metrics.append(
                {
                    "k": k,
                    "n_init": initializations,
                    "seed": seed,
                    "inertia": result["inertia"],
                    "silhouette": result["silhouette_mean"],
                    "ari_hierarchical": float(
                        adjusted_rand_score(hierarchical_reference["labels"], labels)
                    ),
                    "ari_kmeans_reference": float(
                        adjusted_rand_score(kmeans_reference["labels"], labels)
                    ),
                    "smallest_group": int(sizes.min()),
                    "largest_group": int(sizes.max()),
                    "negative_pct": float(100 * (result["silhouette"] < 0).mean()),
                    "iterations": result["iterations"],
                    "iteration_limit_reached": result["iterations"]
                    >= result["parameters"]["max_iter"],
                }
            )
        aris = []
        for (i, a), (j, b) in combinations(enumerate(results), 2):
            ari = float(adjusted_rand_score(a["labels"], b["labels"]))
            aris.append(ari)
            pairs.append((k, initializations, seeds[i], seeds[j], ari))
        stability.append(
            {
                "k": k,
                "n_init": initializations,
                "seeds": len(seeds),
                "ari_min": min(aris),
                "ari_median": float(np.median(aris)),
                "ari_max": max(aris),
                "inertia_min": min(r["inertia"] for r in results),
                "inertia_max": max(r["inertia"] for r in results),
                "silhouette_min": min(r["silhouette_mean"] for r in results),
                "silhouette_max": max(r["silhouette_mean"] for r in results),
            }
        )
        representative = min(results, key=lambda r: r["inertia"])
        name = f"k{k}_n{initializations}"
        representatives.append({"name": name, "result": representative})
        save_case(
            entry, representative, hierarchical_reference["labels"], directory / name
        )
        persistence = pd.concat(
            [
                compare_profiles(representative["labels"], r["labels"]).assign(seed=s)
                for s, r in zip(seeds, results)
            ],
            ignore_index=True,
        )
        persistence.rename(columns=CSV_REPORT_COLUMNS).to_csv(
            directory / name / "profile_persistence.csv", index=False
        )
        persistence.groupby("grupo_representante").agg(
            jaccard_minimo=("jaccard", "min"),
            jaccard_mediano=("jaccard", "median"),
            retencion_minima=("retencion", "min"),
        ).to_csv(directory / name / "profile_stability.csv")
        print(
            f"{name}: minimum pairwise ARI={min(aris):.6f}; "
            f"representative seed={representative['parameters']['random_state']}",
            flush=True,
        )
        # Save progress in case a later batch fails or is interrupted.
        pd.DataFrame(metrics).rename(columns=CSV_REPORT_COLUMNS).to_csv(
            directory / "metrics.csv", index=False
        )
        pd.DataFrame(stability).rename(columns=CSV_REPORT_COLUMNS).to_csv(
            directory / "stability.csv", index=False
        )
        pd.DataFrame(
            pairs, columns=["k", "n_init", "semilla_a", "semilla_b", "ari"]
        ).to_csv(
            directory / "seed_pairs.csv",
            index=False,
        )
        pd.DataFrame(assignments).to_csv(directory / "all_assignments.csv", index=False)
        return min(aris)

    protocol = {
        "analysis_date": entry["analysis_date"],
        "students": len(x),
        "features": list(entry["matrix"].columns),
        "matrix_sha256": sha256(x.tobytes()).hexdigest(),
        "original_values_sha256": sha256(
            pd.util.hash_pandas_object(
                entry["original_values"], index=False
            ).values.tobytes()
        ).hexdigest(),
        "ordered_ids_sha256": sha256(
            pd.util.hash_pandas_object(
                pd.Series(entry["student_ids"]), index=False
            ).values.tobytes()
        ).hexdigest(),
        "reference_parameters": kmeans_reference["parameters"],
        "k_values": list(k_values),
        "seeds": list(seeds),
        "n_init": n_init,
        "n_init_control": n_init_control,
        "control_ari_threshold": control_threshold,
        "representative_selection": "lowest inertia; ties broken by seed order",
        "standardization": "ddof=1; all ten original features, including dropout",
        "state": "running",
    }
    (directory / "protocol.json").write_text(
        json.dumps(protocol, indent=2), encoding="utf-8"
    )
    for k in k_values:
        if batch(k, n_init) < control_threshold:
            batch(k, n_init_control)
    protocol["state"] = "complete"
    (directory / "protocol.json").write_text(
        json.dumps(protocol, indent=2), encoding="utf-8"
    )
    return {
        "metrics": pd.DataFrame(metrics),
        "stability": pd.DataFrame(stability),
        "seed_pairs": pd.DataFrame(
            pairs, columns=["k", "n_init", "semilla_a", "semilla_b", "ari"]
        ),
        "representatives": representatives,
    }


def main() -> None:
    """Load the comparison input and run the explicit experiment protocol."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", dest="date", default="2026-10-01")
    parser.add_argument(
        "--output", dest="output", type=Path, default=Path("output/k-means/exploration")
    )
    parser.add_argument("--k", type=int, nargs="+", default=K_VALUES)
    parser.add_argument("--seeds", dest="seeds", type=int, nargs="+", default=SEEDS)
    parser.add_argument("--n-init", type=int, default=100)
    parser.add_argument("--n-init-control", type=int, default=200)
    args = parser.parse_args()
    entry = prepare_input(analysis_date=args.date)
    result = explore(
        entry,
        args.output,
        k_values=args.k,
        seeds=args.seeds,
        n_init=args.n_init,
        n_init_control=args.n_init_control,
    )
    print(result["stability"].to_string(index=False))
    print(f"Outputs in: {args.output.resolve()}")


if __name__ == "__main__":
    main()
