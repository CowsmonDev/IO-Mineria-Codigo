"""La ejecución básica conserva la entrada y las salidas originales del jerárquico."""

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage
from sklearn.metrics import silhouette_samples

from main import main
from src.clustering import jerarquico


def test_ejecucion_genera_graficos_aunque_dbscan_no_tenga_silhouette(
    entrada, tmp_path, monkeypatch
):
    def referencia_sintetica(matriz, originales):
        # El corte h=35 está fijado para la población real, no para esta muestra pequeña.
        grupos = np.repeat(np.arange(1, 8), 10)
        agrupados = originales.assign(grupo=grupos).groupby("grupo")
        resumen = agrupados.mean()
        resumen.insert(0, "cantidad", agrupados.size())
        valores = silhouette_samples(matriz, grupos)
        return {
            "etiquetas": grupos,
            "enlace": linkage(matriz, method="ward"),
            "resumen": resumen,
            "silhouette": valores,
            "silhouette_promedio": valores.mean(),
            "silhouette_por_k": pd.Series([0.1, 0.2], index=[2, 3]),
            "poblacion_silhouette": len(matriz),
            "motivo_silhouette": "",
            "parametros": {"height": 35},
        }

    monkeypatch.setattr(jerarquico, "analizar", referencia_sintetica)
    def preparar_entrada_sintetica(*, fecha_analisis):
        assert fecha_analisis == "2026-10-01"
        return entrada

    monkeypatch.setattr("main.preparar_entrada", preparar_entrada_sintetica)
    original, matriz = entrada["originales"].copy(), entrada["matriz"].copy()
    resultado = main(fecha="2026-10-01", salida=tmp_path, eps=100, min_samples=5)
    pd.testing.assert_frame_equal(entrada["originales"], original)
    pd.testing.assert_frame_equal(entrada["matriz"], matriz)
    np.testing.assert_array_equal(
        resultado["entrada"]["ids_alumnos"], entrada["ids_alumnos"]
    )
    assert set(resultado["resultados"]) == {"jerarquico", "kmeans", "dbscan"}
    assert resultado["resultados"]["dbscan"]["grupos"] == 1
    for metodo in ("jerarquico", "dbscan", "k-means"):
        assert (tmp_path / metodo / "graficos/silhouette.png").is_file()
        assert (tmp_path / metodo / "graficos/tamanos.png").is_file()
    assert (tmp_path / "dbscan/graficos/vecinos.png").is_file()
    assert (tmp_path / "jerarquico/graficos/dendrograma_general.png").is_file()
    assert not list(tmp_path.glob("*.png"))
    resumen = tmp_path / "jerarquico/resumen_clusters.csv"
    assert pd.read_csv(resumen)["cantidad_observaciones"].sum() == len(original)
    assert list(tmp_path.rglob("*.csv")) == [resumen]
    assert (tmp_path / "jerarquico/graficos/dendrograma_cluster_1.pdf").is_file()
    assert (tmp_path / "jerarquico/graficos/silhouette_por_k.png").is_file()
    assert not list(tmp_path.rglob("*.json"))
