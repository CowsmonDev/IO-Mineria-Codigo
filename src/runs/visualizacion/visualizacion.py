"""Conjuntos de salidas: selecciona gráficos, títulos y rutas por ejecución."""

from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np

from src.data.esquemas import EntradaClustering

from .barras import graficar_barras, graficar_comparacion_barras
from .dendrogramas import graficar_dendrograma, graficar_dendrograma_interno
from .dispersion import graficar_avance_vs_promocionadas, graficar_desercion_por_grupo
from .esquemas import CasoVisualizacion, ResultadoVisualizacion
from .guardado import guardar_figura
from .lineas import graficar_lineas
from .perfiles import graficar_perfil
from .silhouette import graficar_silhouette

CARPETAS = {"jerarquico": "jerarquico", "kmeans": "k-means", "dbscan": "dbscan"}
TITULOS = {"jerarquico": "Jerárquico", "kmeans": "K-Means", "dbscan": "DBSCAN"}


def generar_graficos_ejecucion(
    entrada: EntradaClustering,
    resultado: ResultadoVisualizacion,
    titulo: str,
    carpeta: str | Path,
    *,
    horizontal: bool = False,
) -> None:
    """Arma los gráficos comunes de una configuración y sus vecinos, si existen."""
    carpeta = Path(carpeta)
    resumen = resultado["resumen"]
    etiquetas = ["Ruido" if grupo == -1 else str(grupo) for grupo in resumen.index]
    figura = graficar_barras(
        etiquetas,
        resumen["cantidad"],
        titulo=f"{titulo}: tamaños de grupos",
        xlabel="Grupo",
        ylabel="Estudiantes",
    )
    guardar_figura(figura, carpeta / "tamanos")
    figura = graficar_silhouette(
        resultado["silhouette"],
        resultado["etiquetas"],
        titulo=titulo,
        motivo=resultado["motivo_silhouette"],
    )
    guardar_figura(figura, carpeta / "silhouette")

    originales = entrada["originales"]
    for variable in ("finales_aprobados", "cursadas_promocionadas"):
        if variable in originales:
            figura = graficar_perfil(
                originales,
                resultado["etiquetas"],
                variable,
                titulo=f"{titulo}: {variable}",
                horizontal=horizontal,
            )
            guardar_figura(figura, carpeta / f"perfil_{variable}")
    if "deserto" in originales:
        figura = graficar_barras(
            etiquetas,
            resumen["deserto"],
            titulo=f"{titulo}: deserción por grupo\n(variable incluida en la entrada)",
            xlabel="Grupo",
            ylabel="Proporción de deserción",
            ylim=(0, 1),
        )
        guardar_figura(figura, carpeta / "perfil_deserto")

    if "distancias_vecinos" in resultado:
        m = resultado["parametros"]["min_samples"]
        eps = resultado["parametros"]["eps"]
        distancias = resultado["distancias_vecinos"]
        figura = graficar_lineas(
            np.arange(1, len(distancias) + 1),
            distancias,
            titulo=f"DBSCAN: min_samples={m} (incluye propio punto)",
            xlabel="Observación ordenada",
            ylabel=f"Distancia al vecino {m - 1} externo",
            referencia=eps,
            etiqueta_referencia=f"eps={eps}",
        )
        guardar_figura(figura, carpeta / "vecinos")


def generar_diagnosticos_jerarquicos(
    entrada: EntradaClustering,
    resultado: ResultadoVisualizacion,
    carpeta: str | Path,
) -> None:
    """Agrega los diagnósticos particulares de la referencia jerárquica."""
    carpeta = Path(carpeta)
    altura = resultado["parametros"]["height"]
    figura = graficar_dendrograma(
        resultado["enlace"],
        titulo=f"Jerárquico: Ward y corte a altura {altura}",
        altura_corte=altura,
        ylim=(0, 50),
    )
    guardar_figura(figura, carpeta / "dendrograma_general")
    curva = resultado["silhouette_por_k"]
    figura = graficar_lineas(
        curva.index,
        curva.values,
        titulo="Jerárquico: Silhouette para k=2 a 15",
        xlabel="Número de grupos (k)",
        ylabel="Silhouette promedio",
        marcador="o",
        tamano=(8, 5),
    )
    guardar_figura(figura, carpeta / "silhouette_por_k")

    # Los subgrupos y zooms son diagnósticos; no alteran los grupos originales.
    for grupo in np.unique(resultado["etiquetas"]):
        datos = entrada["matriz"].iloc[np.flatnonzero(resultado["etiquetas"] == grupo)]
        if len(datos) < 3:
            continue
        figura = graficar_dendrograma_interno(
            datos,
            titulo=f"Dendrograma interno - Cluster {grupo}",
            subgrupos=4,
        )
        guardar_figura(
            figura, carpeta / f"dendrograma_cluster_{grupo}", formatos=("png", "pdf")
        )
        if len(datos) >= 500:
            figura = graficar_dendrograma_interno(
                datos.iloc[:50],
                titulo=f"Zoom - Cluster {grupo} (Primeros 50 casos)",
                subgrupos=3,
                tamano=(12, 8),
                etiquetas=True,
            )
            guardar_figura(
                figura,
                carpeta / f"dendrograma_zoom_cluster_{grupo}",
                formatos=("png", "pdf"),
            )

    originales = entrada["originales"]
    rng = np.random.default_rng(1)
    if "deserto" in originales:
        figura = graficar_desercion_por_grupo(
            originales["deserto"],
            resultado["etiquetas"],
            titulo="Distribución de desertores por cluster",
            rng=rng,
        )
        guardar_figura(figura, carpeta / "distribucion_deserto")
    if {"cursadas_promocionadas", "porc_finales", "deserto"}.issubset(
        originales.columns
    ):
        figura = graficar_avance_vs_promocionadas(
            originales,
            titulo="Deserción por cursadas promocionadas y avance de carrera",
            rng=rng,
        )
        guardar_figura(figura, carpeta / "avance_vs_promocionadas")


def generar_graficos_metodos(
    entrada: EntradaClustering,
    resultados: Mapping[str, ResultadoVisualizacion],
    directorio: str | Path,
) -> None:
    """Guarda conjuntos por método en <directorio>/<método>/graficos/."""
    for metodo, resultado in resultados.items():
        carpeta = Path(directorio) / CARPETAS[metodo] / "graficos"
        generar_graficos_ejecucion(
            entrada,
            resultado,
            TITULOS[metodo],
            carpeta,
            horizontal=metodo == "jerarquico",
        )
        if metodo == "jerarquico":
            generar_diagnosticos_jerarquicos(entrada, resultado, carpeta)


def generar_graficos_experimentos_dbscan(
    entrada: EntradaClustering,
    pruebas: Sequence[CasoVisualizacion],
    directorio: str | Path,
) -> None:
    """Guarda cada caso de DBSCAN y la comparación conjunta de sus métricas."""
    raiz = Path(directorio) / "dbscan" / "experimentos"
    for caso in pruebas:
        generar_graficos_ejecucion(
            entrada,
            caso["resultado"],
            f"DBSCAN: {caso['descripcion']}",
            raiz / caso["nombre"] / "graficos",
        )

    nombres = [caso["nombre"] for caso in pruebas]
    resultados = [caso["resultado"] for caso in pruebas]
    ruido = [100 * r["ruido"] / len(entrada["matriz"]) for r in resultados]
    mayores = []
    for resultado in resultados:
        tamanos = resultado["resumen"].drop(index=-1, errors="ignore")["cantidad"]
        mayores.append(100 * tamanos.max() / tamanos.sum() if len(tamanos) else np.nan)
    figura = graficar_comparacion_barras(
        nombres,
        [
            ("Cantidad de grupos (sin ruido)", [r["grupos"] for r in resultados]),
            ("Ruido (% del total)", ruido),
            ("Grupo mayor (% de agrupados)", mayores),
        ],
        titulo=f"DBSCAN: casos fijos sobre la misma entrada ({entrada['fecha_analisis']})",
    )
    guardar_figura(figura, raiz / "graficos" / "comparacion")
