"""Shared console reporting for method runs."""

from src.methods.schemas import ClusteringResult, KMeansResult


def print_result(method: str, result: ClusteringResult | KMeansResult) -> None:
    """Display settings, profiles and Silhouette availability."""
    print(f"\n{method}: {result['parameters']}")
    print(result["summary"].to_string())
    if result["silhouette_reason"]:
        print(result["silhouette_reason"])
    else:
        print(
            f"Silhouette: {result['silhouette_mean']:.6f} over {result['silhouette_population']} students"
        )
    if "noise" in result:
        print(f"Noise: {result['noise']}/{len(result['labels'])} students")
