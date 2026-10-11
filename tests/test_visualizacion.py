"""Los gráficos se pueden reutilizar y exportar fuera de los conjuntos de salida."""

import matplotlib.pyplot as plt
import numpy as np
import pytest

from src.runs.visualizacion.barras import graficar_barras
from src.runs.visualizacion.guardado import guardar_figura
from src.runs.visualizacion.perfiles import graficar_perfil
from src.runs.visualizacion.silhouette import graficar_silhouette


def test_figura_independiente_y_exportacion_a_varios_formatos(tmp_path):
    figura = graficar_barras(
        ["1", "Ruido"], [4, 2], titulo="Tamaños", xlabel="Grupo", ylabel="Estudiantes"
    )
    assert plt.fignum_exists(figura.number)
    assert not list(tmp_path.iterdir())
    assert [barra.get_height() for barra in figura.axes[0].patches] == [4, 2]

    guardar_figura(
        figura, tmp_path / "graficos" / "tamanos.v1", formatos=("png", "pdf")
    )

    assert (tmp_path / "graficos/tamanos.v1.png").read_bytes().startswith(b"\x89PNG")
    assert (tmp_path / "graficos/tamanos.v1.pdf").read_bytes().startswith(b"%PDF")
    assert not plt.fignum_exists(figura.number)


def test_silhouette_sin_valores_explica_el_motivo():
    figura = graficar_silhouette(
        [np.nan, np.nan], [-1, -1], titulo="DBSCAN", motivo="Todos son ruido"
    )
    try:
        assert figura.axes[0].texts[0].get_text() == "Todos son ruido"
        assert "no disponible" in figura.axes[0].get_title()
    finally:
        plt.close(figura)


@pytest.mark.parametrize("horizontal", [False, True])
def test_perfil_rotula_los_ejes_segun_su_orientacion(entrada, horizontal):
    figura = graficar_perfil(
        entrada["originales"],
        np.repeat(np.arange(7), 10),
        "finales_aprobados",
        titulo="Perfil",
        horizontal=horizontal,
    )
    try:
        ax = figura.axes[0]
        assert ax.get_xlabel() == ("finales_aprobados" if horizontal else "Grupo")
        assert ax.get_ylabel() == ("Grupo" if horizontal else "finales_aprobados")
    finally:
        plt.close(figura)
