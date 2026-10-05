"""Gráficos comunes y diagnósticos de los tres algoritmos."""

from textwrap import fill

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist


def generar(entrada, resultados, directorio):
    """Guarda las figuras en <directorio>/<método>/graficos/."""
    carpetas = {"jerarquico": "jerarquico", "kmeans": "k-means", "dbscan": "dbscan"}
    titulos = {"jerarquico": "Jerárquico", "kmeans": "K-Means", "dbscan": "DBSCAN"}

    def guardar(fig, metodo, nombre):
        carpeta = directorio / carpetas[metodo] / "graficos"
        carpeta.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(carpeta / f"{nombre}.png", dpi=160, bbox_inches="tight")
        plt.close(fig)

    def etiqueta(grupo):
        return "Ruido" if grupo == -1 else str(grupo)

    for metodo, resultado in resultados.items():
        titulo = titulos[metodo]
        tabla = resultado["resumen"]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar([etiqueta(g) for g in tabla.index], tabla["cantidad"])
        ax.set(
            title=f"{titulo}: tamaños de grupos", xlabel="Grupo", ylabel="Estudiantes"
        )
        guardar(fig, metodo, "tamanos")

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
                ax.fill_betweenx(
                    np.arange(inicio, inicio + len(ordenados)), 0, ordenados
                )
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
        guardar(fig, metodo, "silhouette")

        for variable in ("finales_aprobados", "cursadas_promocionadas"):
            if variable not in entrada["originales"]:
                continue
            fig, ax = plt.subplots(figsize=(8, 6))
            tabla = (
                entrada["originales"][[variable]]
                .reset_index(drop=True)
                .assign(grupo=[etiqueta(g) for g in resultado["etiquetas"]])
            )
            sns.boxplot(data=tabla, x="grupo", y=variable, ax=ax)
            ax.set(title=f"{titulo}: {variable}", xlabel="Grupo")
            guardar(fig, metodo, f"perfil_{variable}")
        if "deserto" in entrada["originales"]:
            fig, ax = plt.subplots(figsize=(8, 5))
            medias = resultado["resumen"]["deserto"]
            ax.bar([etiqueta(g) for g in medias.index], medias)
            ax.set(
                title=f"{titulo}: deserción por grupo\n(variable incluida en la entrada)",
                xlabel="Grupo",
                ylabel="Proporción de deserción",
                ylim=(0, 1),
            )
            guardar(fig, metodo, "perfil_deserto")

    db = resultados["dbscan"]
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
    guardar(fig, "dbscan", "vecinos")

    fig, ax = plt.subplots(figsize=(10, 6))
    dendrogram(
        resultados["jerarquico"]["enlace"], color_threshold=35, no_labels=True, ax=ax
    )
    ax.axhline(35, linestyle="--", color="red")
    ax.set(title="Jerárquico: Ward y corte a altura 35", ylabel="Altura", ylim=(0, 50))
    guardar(fig, "jerarquico", "dendrograma_general")
    # Mantener los dendrogramas internos útiles, sin convertir sus subgrupos en nuevas etiquetas.
    for grupo in np.unique(resultados["jerarquico"]["etiquetas"]):
        datos = entrada["matriz"].iloc[
            np.flatnonzero(resultados["jerarquico"]["etiquetas"] == grupo)
        ]
        if len(datos) < 3:
            continue
        fig, ax = plt.subplots(figsize=(12, 7))
        dendrogram(linkage(pdist(datos), method="ward"), no_labels=True, ax=ax)
        ax.set(title=f"Dendrograma interno: grupo {grupo}", ylabel="Altura")
        guardar(fig, "jerarquico", f"dendrograma_grupo_{grupo}")
