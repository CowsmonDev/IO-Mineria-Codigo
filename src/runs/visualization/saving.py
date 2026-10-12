"""Shared figure export to disk."""

from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def save_figure(
    figure: Figure,
    path: str | Path,
    *,
    formats: Sequence[str] = ("png",),
    dpi: int = 160,
) -> None:
    """Save the requested formats and close the figure.

    The path is a base filename without an extension. Plot builders return open
    figures; callers must save them here or close them explicitly."""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.tight_layout()
        for format in formats:
            figure.savefig(
                path.parent / f"{path.name}.{format}",
                format=format,
                dpi=dpi,
                bbox_inches="tight",
            )
    finally:
        plt.close(figure)
