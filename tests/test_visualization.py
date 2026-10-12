"""Plots can be reused and exported independently of output bundles."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

from src.data.constants import Columns
from src.data.schemas import ClusteringInput
from src.runs.visualization.bars import plot_bars
from src.runs.visualization.profiles import plot_profile
from src.runs.visualization.saving import save_figure
from src.runs.visualization.silhouette import plot_silhouette


def test_standalone_figure_and_multiple_export_formats(tmp_path: Path) -> None:
    figure = plot_bars(
        ["1", "Noise"], [4, 2], title="Group sizes", xlabel="Group", ylabel="Students"
    )
    assert plt.fignum_exists(figure.number)
    assert not list(tmp_path.iterdir())
    assert [bar.get_height() for bar in figure.axes[0].patches] == [4, 2]

    save_figure(figure, tmp_path / "plots" / "sizes.v1", formats=("png", "pdf"))

    assert (tmp_path / "plots/sizes.v1.png").read_bytes().startswith(b"\x89PNG")
    assert (tmp_path / "plots/sizes.v1.pdf").read_bytes().startswith(b"%PDF")
    assert not plt.fignum_exists(figure.number)


def test_empty_silhouette_explains_reason() -> None:
    figure = plot_silhouette(
        [np.nan, np.nan], [-1, -1], title="DBSCAN", reason="All observations are noise"
    )
    try:
        assert figure.axes[0].texts[0].get_text() == "All observations are noise"
        assert "unavailable" in figure.axes[0].get_title()
    finally:
        plt.close(figure)


@pytest.mark.parametrize("horizontal", [False, True])
def test_profile_labels_axes_for_orientation(
    entry: ClusteringInput, horizontal: bool
) -> None:
    figure = plot_profile(
        entry["original_values"],
        np.repeat(np.arange(7), 10),
        Columns.PASSED_FINALS,
        title="Profile",
        horizontal=horizontal,
    )
    try:
        ax = figure.axes[0]
        assert ax.get_xlabel() == (Columns.PASSED_FINALS if horizontal else "Group")
        assert ax.get_ylabel() == ("Group" if horizontal else Columns.PASSED_FINALS)
    finally:
        plt.close(figure)
