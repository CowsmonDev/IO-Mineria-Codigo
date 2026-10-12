"""Experiment contracts; TypedDict describes types without validating data."""

from typing import Generic, TypedDict, TypeVar

import pandas as pd

from src.data.schemas import ClusteringInput
from src.methods.schemas import ClusteringResult, KMeansResult


class KMeansCase(TypedDict):
    """Identified fit retained for profile and correspondence interpretation."""

    name: str
    result: KMeansResult


class KMeansExploration(TypedDict):
    """Experiment tables and representative fits without an automatic winner."""

    metrics: pd.DataFrame
    stability: pd.DataFrame
    seed_pairs: pd.DataFrame
    representatives: list[KMeansCase]


class KMeansMetric(TypedDict):
    """Metrics for one configuration and seed."""

    k: int
    n_init: int
    seed: int
    inertia: float
    silhouette: float
    ari_hierarchical: float
    ari_kmeans_reference: float
    smallest_group: int
    largest_group: int
    negative_pct: float
    iterations: int
    iteration_limit_reached: bool


class KMeansStability(TypedDict):
    """Initialization sensitivity measured across pairs of seeds."""

    k: int
    n_init: int
    seeds: int
    ari_min: float
    ari_median: float
    ari_max: float
    inertia_min: float
    inertia_max: float
    silhouette_min: float
    silhouette_max: float


ResultT = TypeVar("ResultT", bound=ClusteringResult | KMeansResult)


class ClusteringCase(TypedDict, Generic[ResultT]):
    """Identified configuration of a clustering method."""

    name: str
    description: str
    result: ResultT


class ClusteringRun(TypedDict, Generic[ResultT]):
    """Main fit and cases of the method protocol."""

    result: ResultT
    cases: list[ClusteringCase[ResultT]]


class MethodResults(TypedDict):
    """Results of all three methods on the same input."""

    hierarchical: ClusteringResult
    kmeans: KMeansResult
    dbscan: ClusteringResult


class ComparisonResult(TypedDict):
    """Aligned input, reference fits and fixed DBSCAN cases."""

    entry: ClusteringInput
    results: MethodResults
    dbscan_cases: list[ClusteringCase[ClusteringResult]]
