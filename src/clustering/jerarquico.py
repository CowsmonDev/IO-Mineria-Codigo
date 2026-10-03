"""Referencia jerárquica, dendrogramas, resumen y validación originales."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from scipy.cluster.hierarchy import cut_tree, dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import silhouette_samples, silhouette_score


def analizar(alumnos_s_avanzados, alumnos_s_avanzados_sc):
    """Agrupa con Ward a altura 35 y exporta las salidas de referencia."""
    alumnos_s_avanzados = alumnos_s_avanzados.copy()
    _directorio_graficos = Path("output/graficos/02_analisis_preliminar")
    _directorio_graficos.mkdir(parents=True, exist_ok=True)

    def _guardar_grafico(figura, nombre):
        figura.savefig(
            _directorio_graficos / f"{nombre}.png", dpi=160, bbox_inches="tight"
        )

    # Creación de la matriz de distancias y clustering jerárquico
    # Calcula las distancias euclideanas entre estudiantes.
    # Corta el dendrograma a una altura h = 35 para formar los clusters.

    alumnos_s_avanzados_dist_mat = pdist(
        alumnos_s_avanzados_sc.to_numpy(), metric="euclidean"
    )
    # Enlace Ward.D2 de R: en SciPy se utiliza method="ward".
    hclust_alumnos_s_avanzados = linkage(alumnos_s_avanzados_dist_mat, method="ward")
    hclustered_alumnos_s_avanzados = (
        cut_tree(hclust_alumnos_s_avanzados, height=35).reshape(-1) + 1
    )

    # Visualización del dendrograma
    # Muestra el árbol de decisión jerárquico coloreado por grupo.
    # Ayuda a visualizar cómo se formaron los clusters.

    fig_dendrograma, ax_dendrograma = plt.subplots()
    dendrogram(
        hclust_alumnos_s_avanzados,
        color_threshold=35,
        no_labels=True,
        ax=ax_dendrograma,
    )
    ax_dendrograma.set_ylim(0, 50)

    # Actualización del dataframe con la información del cluster -> Asignación del cluster a cada alumno
    alumnos_s_avanzados["cluster"] = pd.Categorical(hclustered_alumnos_s_avanzados)

    # Creación de un resumen de los clusters -> Resumen estadístico por cluster
    # Muestra cómo se comportan las variables clave en cada cluster: si son más desertores, si promocionan más materias, etc.

    resumen_cluster = (
        alumnos_s_avanzados.groupby("cluster", as_index=False, observed=True)
        .agg(
            cantidad_observaciones=("cluster", "size"),
            media_cursadas_aprobadas=("cursadas_aprobadas", "mean"),
            media_cursadas_desaprobadas=("cursadas_desaprobadas", "mean"),
            media_materias_anotado_ult_anio=("materias_anotado_ult_anio", "mean"),
            media_finales_aprobados=("finales_aprobados", "mean"),
            media_finales_desaprobados=("finales_desaprobados", "mean"),
            media_cursadas_promocionadas=("cursadas_promocionadas", "mean"),
            media_porc_finales=("porc_finales", "mean"),
            media_T_desde_ingreso=("tiempo_desde_ingreso", "mean"),
            media_deserto=("deserto", "mean"),
            media_dias_dsd_ultimo_final=("dias_dsd_ultimo_final", "mean"),
        )
        .copy()
    )

    _guardar_grafico(fig_dendrograma, "dendrograma_general")

    # Dendrogramas de cada clúster

    # =====================================
    # NUEVO: Dendrogramas individuales por cluster
    # =====================================

    # Crear carpeta de salida si no existe
    Path("output/dendrogramas").mkdir(parents=True, exist_ok=True)

    # Los nombres de fila de alumnos_s_avanzados_sc se asignaron de 1 a n para mantener trazabilidad.

    # Generar dendrogramas internos y exportar como PDF
    for k in sorted(alumnos_s_avanzados["cluster"].unique()):
        print("Generando dendrograma para cluster:", k)
        idx = alumnos_s_avanzados["cluster"].astype(int).to_numpy() == k
        datos_cluster = alumnos_s_avanzados_sc.iloc[np.flatnonzero(idx)]

        if len(datos_cluster) > 2:
            dist_cl = pdist(datos_cluster.to_numpy())
            hc_cl = linkage(dist_cl, method="ward")

            # Cortar en 4 subgrupos internos para análisis
            subgrupos = cut_tree(hc_cl, n_clusters=4).reshape(-1) + 1

            # Guardar dendrograma completo con rectángulos por subgrupo
            fig_cluster, ax_cluster = plt.subplots(figsize=(15, 10))
            dend_cluster = dendrogram(
                hc_cl,
                no_labels=True,
                ax=ax_cluster,
            )
            ax_cluster.set_title(f"Dendrograma interno - Cluster {k}")
            ax_cluster.set_ylabel("Altura (distancia)")

            posiciones_hojas = {
                hoja: 5 + posicion * 10
                for posicion, hoja in enumerate(dend_cluster["leaves"])
            }
            altura_rectangulos = hc_cl[-3, 2]
            colores_rectangulos = ["red", "green", "blue", "cyan"]
            grupos_con_posicion = []
            for grupo in np.unique(subgrupos):
                posicion_inicial = min(
                    posiciones_hojas[indice]
                    for indice in np.flatnonzero(subgrupos == grupo)
                )
                grupos_con_posicion.append((posicion_inicial, grupo))
            grupos_ordenados = [grupo for _, grupo in sorted(grupos_con_posicion)]
            for numero_grupo, grupo in enumerate(grupos_ordenados):
                posiciones_grupo = [
                    posiciones_hojas[indice]
                    for indice in np.flatnonzero(subgrupos == grupo)
                ]
                ax_cluster.add_patch(
                    Rectangle(
                        (min(posiciones_grupo) - 4, 0),
                        max(posiciones_grupo) - min(posiciones_grupo) + 8,
                        altura_rectangulos,
                        fill=False,
                        edgecolor=colores_rectangulos[numero_grupo],
                    )
                )

            fig_cluster.savefig(
                f"output/dendrogramas/dendrograma_cluster_{k}.pdf",
                format="pdf",
            )
            _guardar_grafico(fig_cluster, f"dendrograma_cluster_{k}")
            plt.close(fig_cluster)

            # Guardar dendrograma con zoom (primeros 50 casos si hay suficientes)
            if len(datos_cluster) >= 500:
                datos_subset = datos_cluster.iloc[:50]
                hc_subset = linkage(pdist(datos_subset.to_numpy()), method="ward")
                subgrupos_subset = cut_tree(hc_subset, n_clusters=3).reshape(-1) + 1

                fig_subset, ax_subset = plt.subplots(figsize=(12, 8))
                dend_subset = dendrogram(
                    hc_subset,
                    labels=datos_subset.index.astype(str).to_list(),
                    leaf_font_size=7,
                    ax=ax_subset,
                )
                ax_subset.set_title(f"Zoom - Cluster {k} (Primeros 50 casos)")
                ax_subset.set_ylabel("Altura (distancia)")

                posiciones_hojas_subset = {
                    hoja: 5 + posicion * 10
                    for posicion, hoja in enumerate(dend_subset["leaves"])
                }
                altura_rectangulos_subset = hc_subset[-2, 2]
                grupos_subset_con_posicion = []
                for grupo in np.unique(subgrupos_subset):
                    posicion_inicial = min(
                        posiciones_hojas_subset[indice]
                        for indice in np.flatnonzero(subgrupos_subset == grupo)
                    )
                    grupos_subset_con_posicion.append((posicion_inicial, grupo))
                grupos_subset_ordenados = [
                    grupo for _, grupo in sorted(grupos_subset_con_posicion)
                ]
                for numero_grupo, grupo in enumerate(grupos_subset_ordenados):
                    posiciones_grupo = [
                        posiciones_hojas_subset[indice]
                        for indice in np.flatnonzero(subgrupos_subset == grupo)
                    ]
                    ax_subset.add_patch(
                        Rectangle(
                            (min(posiciones_grupo) - 4, 0),
                            max(posiciones_grupo) - min(posiciones_grupo) + 8,
                            altura_rectangulos_subset,
                            fill=False,
                            edgecolor=colores_rectangulos[numero_grupo],
                        )
                    )

                fig_subset.savefig(
                    f"output/dendrogramas/dendrograma_zoom_cluster_{k}.pdf",
                    format="pdf",
                )
                _guardar_grafico(fig_subset, f"dendrograma_zoom_cluster_{k}")
                plt.close(fig_subset)
        else:
            print("Cluster", k, "tiene muy pocos elementos para dendrograma.")

    # Exportación del resumen de clústeres

    # Para exportar el resumen de los clusters formados por el clustering jerarquico
    resumen_cluster_exportacion = resumen_cluster.copy()
    resumen_cluster_exportacion["cluster"] = resumen_cluster_exportacion[
        "cluster"
    ].astype(str)
    resumen_cluster_exportacion.to_csv(
        "resumen_clusters.csv",
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )

    # Validación con Silhouette

    # ------------------------------
    # Validación de agrupamientos
    # ------------------------------

    # Silhouette para jerárquico
    _matriz_distancias = squareform(alumnos_s_avanzados_dist_mat)
    _clusters_jerarquicos = alumnos_s_avanzados["cluster"].astype(int).to_numpy()
    sil_h = silhouette_samples(
        _matriz_distancias,
        _clusters_jerarquicos,
        metric="precomputed",
    )

    fig_silhouette, ax_silhouette = plt.subplots()
    posicion_inferior = 10
    for k in sorted(np.unique(_clusters_jerarquicos)):
        valores_cluster = np.sort(sil_h[_clusters_jerarquicos == k])
        posicion_superior = posicion_inferior + len(valores_cluster)
        ax_silhouette.fill_betweenx(
            np.arange(posicion_inferior, posicion_superior),
            0,
            valores_cluster,
        )
        ax_silhouette.text(-0.05, posicion_inferior + len(valores_cluster) / 2, str(k))
        posicion_inferior = posicion_superior + 10
    ax_silhouette.set_title("Silhouette - Jerárquico")
    ax_silhouette.set_xlabel("Ancho de silhouette")
    ax_silhouette.set_ylabel("Cluster")

    ###########################################################
    # Encontrar el mejor valor de k, usando Silhouette Score
    ###########################################################

    sil_scores = np.full(16, np.nan)
    for k in range(2, 16):
        clust_temp = cut_tree(hclust_alumnos_s_avanzados, n_clusters=k).reshape(-1) + 1
        sil_scores[k] = silhouette_score(
            _matriz_distancias,
            clust_temp,
            metric="precomputed",
        )

    # Graficar resultados
    fig_sil_scores, ax_sil_scores = plt.subplots()
    ax_sil_scores.plot(range(2, 16), sil_scores[2:16], marker="o")
    ax_sil_scores.set_xlabel("Número de clústeres (k)")
    ax_sil_scores.set_ylabel("Silhouette promedio")
    ax_sil_scores.set_title("Silhouette score para cada k")

    _guardar_grafico(fig_silhouette, "silhouette_jerarquico")
    _guardar_grafico(fig_sil_scores, "silhouette_por_k")

    return {
        "alumnos_s_avanzados": alumnos_s_avanzados,
        "alumnos_s_avanzados_dist_mat": alumnos_s_avanzados_dist_mat,
    }
