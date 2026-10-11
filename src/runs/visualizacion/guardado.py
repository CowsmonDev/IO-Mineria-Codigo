"""Exportación común de figuras a disco."""

from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def guardar_figura(
    figura: Figure,
    ruta: str | Path,
    *,
    formatos: Sequence[str] = ("png",),
    dpi: int = 160,
) -> None:
    """Guarda una figura en los formatos pedidos y la cierra.

    ruta es el nombre base sin extensión. Las funciones de dibujo devuelven
    figuras abiertas; quien las utiliza debe guardarlas aquí o cerrarlas.
    """
    ruta = Path(ruta)
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        figura.tight_layout()
        for formato in formatos:
            figura.savefig(
                ruta.parent / f"{ruta.name}.{formato}",
                format=formato,
                dpi=dpi,
                bbox_inches="tight",
            )
    finally:
        plt.close(figura)
