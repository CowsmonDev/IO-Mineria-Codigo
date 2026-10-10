"""Gráficos comunes y diagnósticos de los tres algoritmos."""

from textwrap import fill

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.patches import Rectangle
from scipy.cluster.hierarchy import cut_tree, dendrogram, linkage
from scipy.spatial.distance import pdist


def _generar_individual(entrada, resultado, titulo, carpeta, *, jerarquico=False):
    """Gráficos de una ejecución, sin volver a ajustar el algoritmo."""

    def guardar(fig, nombre):
        carpeta.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(carpeta / f"{nombre}.png", dpi=160, bbox_inches="tight")
        plt.close(fig)

    def etiqueta(grupo):
        return "Ruido" if grupo == -1 else str(grupo)

    tabla = resultado["resumen"]
    ancho = min(24, max(8, len(tabla) * 0.35))
    fig, ax = plt.subplots(figsize=(ancho, 5))
    ax.bar([etiqueta(g) for g in tabla.index], tabla["cantidad"])
    ax.set(title=f"{titulo}: tamaños de grupos", xlabel="Grupo", ylabel="Estudiantes")
    if len(tabla) > 15:
        ax.tick_params(axis="x", labelrotation=90, labelsize=8)
    guardar(fig, "tamanos")

    fig, ax = plt.subplots(figsize=(8, 6))
    valores = resultado["silhouette"]
    if not np.isfinite(valores).any():
        ax.text(
            0.5,
            0.5,
            fill(resultado["motivo_silhouette"], width=48),
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        ax.set(title=f"{titulo}: Silhouette no disponible", yticks=[], xticks=[])
    else:
        inicio = 0
        for grupo in np.unique(resultado["etiquetas"]):
            if grupo == -1:
                continue
            ordenados = np.sort(valores[resultado["etiquetas"] == grupo])
            ax.fill_betweenx(np.arange(inicio, inicio + len(ordenados)), 0, ordenados)
            ax.text(-0.95, inicio + len(ordenados) / 2, str(grupo))
            inicio += len(ordenados) + 10
        n = np.isfinite(valores).sum()
        ax.axvline(np.nanmean(valores), color="red", linestyle="--")
        ax.set(
            title=f"{titulo}: Silhouette {np.nanmean(valores):.4f}\n{n}/{len(valores)} estudiantes",
            xlim=(-1, 1),
            xlabel="Silhouette",
            yticks=[],
        )
    guardar(fig, "silhouette")

    for variable in ("finales_aprobados", "cursadas_promocionadas"):
        if variable not in entrada["originales"]:
            continue
        fig, ax = plt.subplots(figsize=(ancho, 6))
        tabla = (
            entrada["originales"][[variable]]
            .reset_index(drop=True)
            .assign(grupo=[etiqueta(g) for g in resultado["etiquetas"]])
        )
        if jerarquico:
            sns.boxplot(data=tabla, x=variable, y="grupo", orient="h", ax=ax)
        else:
            sns.boxplot(data=tabla, x="grupo", y=variable, ax=ax)
            if tabla["grupo"].nunique() > 15:
                ax.tick_params(axis="x", labelrotation=90, labelsize=8)
        ax.set(title=f"{titulo}: {variable}", xlabel="Grupo")
        guardar(fig, f"perfil_{variable}")
    if "deserto" in entrada["originales"]:
        fig, ax = plt.subplots(figsize=(ancho, 5))
        medias = resultado["resumen"]["deserto"]
        ax.bar([etiqueta(g) for g in medias.index], medias)
        ax.set(
            title=f"{titulo}: deserción por grupo\n(variable incluida en la entrada)",
            xlabel="Grupo",
            ylabel="Proporción de deserción",
            ylim=(0, 1),
        )
        if len(medias) > 15:
            ax.tick_params(axis="x", labelrotation=90, labelsize=8)
        guardar(fig, "perfil_deserto")

    if "distancias_vecinos" not in resultado:
        return
    db = resultado
    fig, ax = plt.subplots(figsize=(9, 5))
    m, eps = db["parametros"]["min_samples"], db["parametros"]["eps"]
    ax.plot(np.arange(1, len(db["distancias_vecinos"]) + 1), db["distancias_vecinos"])
    ax.axhline(eps, color="red", linestyle="--", label=f"eps={eps}")
    ax.set(
        title=f"DBSCAN: min_samples={m} (incluye propio punto)",
        xlabel="Observación ordenada",
        ylabel=f"Distancia al vecino {m - 1} externo",
    )
    ax.legend()
    guardar(fig, "vecinos")


def generar(entrada, resultados, directorio):
    """Guarda las figuras en <directorio>/<método>/graficos/."""
    carpetas = {"jerarquico": "jerarquico", "kmeans": "k-means", "dbscan": "dbscan"}
    titulos = {"jerarquico": "Jerárquico", "kmeans": "K-Means", "dbscan": "DBSCAN"}

    def guardar(fig, metodo, nombre, *, pdf=False):
        carpeta = directorio / carpetas[metodo] / "graficos"
        carpeta.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(carpeta / f"{nombre}.png", dpi=160, bbox_inches="tight")
        if pdf:
            fig.savefig(carpeta / f"{nombre}.pdf", format="pdf", bbox_inches="tight")
        plt.close(fig)

    for metodo, resultado in resultados.items():
        _generar_individual(
            entrada,
            resultado,
            titulos[metodo],
            directorio / carpetas[metodo] / "graficos",
            jerarquico=metodo == "jerarquico",
        )

    fig, ax = plt.subplots(figsize=(10, 6))
    dendrogram(
        resultados["jerarquico"]["enlace"], color_threshold=35, no_labels=True, ax=ax
    )
    ax.axhline(35, linestyle="--", color="red")
    ax.set(title="Jerárquico: Ward y corte a altura 35", ylabel="Altura", ylim=(0, 50))
    guardar(fig, "jerarquico", "dendrograma_general")
    curva = resultados["jerarquico"]["silhouette_por_k"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(curva.index, curva.values, marker="o")
    ax.set(
        title="Jerárquico: Silhouette para k=2 a 15",
        xlabel="Número de grupos (k)",
        ylabel="Silhouette promedio",
    )
    guardar(fig, "jerarquico", "silhouette_por_k")

    def dendrograma_interno(datos, *, titulo, subgrupos, tamano, etiquetas=False):
        enlace = linkage(pdist(datos.to_numpy()), method="ward")
        fig, ax = plt.subplots(figsize=tamano)
        dibujo = dendrogram(
            enlace,
            no_labels=not etiquetas,
            labels=datos.index.astype(str).tolist() if etiquetas else None,
            leaf_font_size=7,
            ax=ax,
        )
        ax.set(title=titulo, ylabel="Altura (distancia)")
        k = min(subgrupos, len(datos))
        grupos = cut_tree(enlace, n_clusters=k).reshape(-1)
        posiciones = {hoja: 5 + i * 10 for i, hoja in enumerate(dibujo["leaves"])}
        orden = sorted(
            np.unique(grupos),
            key=lambda grupo: min(
                posiciones[i] for i in np.flatnonzero(grupos == grupo)
            ),
        )
        superior = enlace[len(datos) - k, 2]
        inferior = enlace[len(datos) - k - 1, 2] if len(datos) > k else 0
        altura = (superior + inferior) / 2
        for grupo, color in zip(orden, ("red", "green", "blue", "cyan")):
            xs = [posiciones[i] for i in np.flatnonzero(grupos == grupo)]
            ax.add_patch(
                Rectangle(
                    (min(xs) - 4, 0),
                    max(xs) - min(xs) + 8,
                    altura,
                    fill=False,
                    edgecolor=color,
                )
            )
        return fig

    # Los subgrupos y zooms son diagnósticos y no alteran los siete grupos originales.
    for grupo in np.unique(resultados["jerarquico"]["etiquetas"]):
        datos = entrada["matriz"].iloc[
            np.flatnonzero(resultados["jerarquico"]["etiquetas"] == grupo)
        ]
        if len(datos) < 3:
            continue
        fig = dendrograma_interno(
            datos,
            titulo=f"Dendrograma interno - Cluster {grupo}",
            subgrupos=4,
            tamano=(15, 10),
        )
        guardar(fig, "jerarquico", f"dendrograma_cluster_{grupo}", pdf=True)
        if len(datos) >= 500:
            fig = dendrograma_interno(
                datos.iloc[:50],
                titulo=f"Zoom - Cluster {grupo} (Primeros 50 casos)",
                subgrupos=3,
                tamano=(12, 8),
                etiquetas=True,
            )
            guardar(fig, "jerarquico", f"dendrograma_zoom_cluster_{grupo}", pdf=True)

    originales = entrada["originales"]
    rng = np.random.default_rng(1)
    if "deserto" in originales:
        fig, ax = plt.subplots(figsize=(8, 6))
        grupos = resultados["jerarquico"]["etiquetas"]
        for posicion, grupo in enumerate(np.unique(grupos)):
            valores = originales.loc[grupos == grupo, "deserto"].to_numpy()
            ax.scatter(
                valores + rng.uniform(-0.15, 0.15, len(valores)),
                posicion + rng.uniform(-0.25, 0.25, len(valores)),
                alpha=0.75,
            )
        ax.set(
            title="Distribución de desertores por cluster",
            xlabel="Deserto (1: sí; 0: no)",
            ylabel="Cluster",
            xticks=[0, 1],
            yticks=range(len(np.unique(grupos))),
            yticklabels=np.unique(grupos),
        )
        guardar(fig, "jerarquico", "distribucion_deserto")
    if {"cursadas_promocionadas", "porc_finales", "deserto"}.issubset(
        originales.columns
    ):
        fig, ax = plt.subplots(figsize=(9, 6))
        for valor, datos in originales.groupby("deserto"):
            ax.scatter(
                datos["cursadas_promocionadas"] + rng.uniform(-0.3, 0.3, len(datos)),
                datos["porc_finales"] + rng.uniform(-0.05, 0.05, len(datos)),
                alpha=0.8,
                label=str(int(valor)),
            )
        ax.set(
            title="Deserción por cursadas promocionadas y avance de carrera",
            xlabel="Cursadas promocionadas",
            ylabel="Avance de carrera",
        )
        ax.legend(title="Deserto (1: sí; 0: no)")
        guardar(fig, "jerarquico", "avance_vs_promocionadas")


def generar_pruebas_dbscan(entrada, pruebas, directorio):
    """Guarda cada caso en dbscan/experimentos/<nombre>/graficos/."""
    raiz = directorio / "dbscan" / "experimentos"
    for caso in pruebas:
        _generar_individual(
            entrada,
            caso["resultado"],
            f"DBSCAN: {caso['descripcion']}",
            raiz / caso["nombre"] / "graficos",
        )

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    nombres = [caso["nombre"] for caso in pruebas]
    resultados = [caso["resultado"] for caso in pruebas]
    ruido = [100 * r["ruido"] / len(entrada["matriz"]) for r in resultados]
    mayores = []
    for resultado in resultados:
        tamanos = resultado["resumen"].drop(index=-1, errors="ignore")["cantidad"]
        mayores.append(100 * tamanos.max() / tamanos.sum() if len(tamanos) else np.nan)
    for ax, valores, titulo in zip(
        axes,
        ([r["grupos"] for r in resultados], ruido, mayores),
        (
            "Cantidad de grupos (sin ruido)",
            "Ruido (% del total)",
            "Grupo mayor (% de agrupados)",
        ),
    ):
        barras = ax.barh(nombres, valores)
        ax.bar_label(
            barras,
            labels=[f"{v:.1f}" if np.isfinite(v) else "Sin agrupados" for v in valores],
            padding=3,
        )
        finitos = [v for v in valores if np.isfinite(v)]
        ax.set(title=titulo, xlim=(0, max([1, *finitos]) * 1.2))
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.2)
    fig.suptitle(
        f"DBSCAN: casos fijos sobre la misma entrada ({entrada['fecha_analisis']})"
    )
    carpeta = raiz / "graficos"
    carpeta.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(carpeta / "comparacion.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
