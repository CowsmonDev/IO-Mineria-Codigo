"""Independent LASSO logistic regression run."""

from src.data.preparation import prepare_input
from src.methods.lasso import analyze
from src.methods.schemas import LassoResult


def main(*, analysis_date: str | None = None) -> LassoResult:
    """Run the LASSO baseline separately from the clustering comparison."""
    entry = prepare_input(analysis_date=analysis_date)
    return analyze(entry["original_values"])


if __name__ == "__main__":
    main()
