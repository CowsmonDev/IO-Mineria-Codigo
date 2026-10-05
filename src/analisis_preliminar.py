"""Coordina preparación, LASSO, jerárquico y gráficos descriptivos originales."""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .clustering.jerarquico import analizar as analizar_jerarquico
from .data.manipulacion import main as preparar_datos
from .data.preparacion import estandarizar, preparar_variables
from .lasso import analizar as analizar_lasso


def main(datos=None):
    """Analiza los datos recibidos o ejecuta primero su preparación."""
    if datos is None:
        datos = preparar_datos()
    # Generar archivos de imagen sin abrir ventanas.
    plt.switch_backend("Agg")
    os.chdir(Path(__file__).resolve().parents[1])

    alumnos_s_avanzados = datos["alumnos_s_avanzados"]
    alumnos_s_avanzados_desaprob_mat_IS = datos["alumnos_s_avanzados_desaprob_mat_IS"]
    alumnos_desertores = datos["alumnos_desertores"]

    # Guardar los gráficos como archivos PNG.
    _directorio_graficos = Path("output/graficos/02_analisis_preliminar")
    _directorio_graficos.mkdir(parents=True, exist_ok=True)

    def _guardar_grafico(figura, nombre):
        figura.savefig(
            _directorio_graficos / f"{nombre}.png", dpi=160, bbox_inches="tight"
        )

    # Porcentajes descriptivos

    # Análisis de desertores que desaprobaron materias importantes de Ingeniería en Sistemas

    print(
        pd.DataFrame(
            {
                "porc_desertores": [
                    (alumnos_s_avanzados_desaprob_mat_IS["deserto"] == True).mean()
                    * 100
                ]
            }
        )
    )

    # Análisis de desertores que nacieron en la localidad de Tandil (donde se cursa la carrera)

    print(
        pd.DataFrame(
            {
                "porc_desertores_fuera_tandil": [
                    (
                        (alumnos_desertores["deserto"] == True)
                        & (alumnos_desertores["localidad_nacimiento"] != "TANDIL")
                    ).mean()
                    * 100
                ]
            }
        )
    )

    # Guardar la identidad antes de quitar id_alumno de las variables numéricas.
    ids_alumnos = alumnos_s_avanzados["id_alumno"].to_numpy(copy=True)
    alumnos_s_avanzados = preparar_variables(alumnos_s_avanzados)
    analizar_lasso(alumnos_s_avanzados)

    # Conservar la semilla y el orden del análisis original.
    np.random.seed(1)
    alumnos_s_avanzados_sc = estandarizar(alumnos_s_avanzados)
    resultados_jerarquicos = analizar_jerarquico(
        alumnos_s_avanzados, alumnos_s_avanzados_sc
    )
    alumnos_s_avanzados = resultados_jerarquicos["alumnos_s_avanzados"]
    alumnos_s_avanzados_dist_mat = resultados_jerarquicos[
        "alumnos_s_avanzados_dist_mat"
    ]

    # Visualización de perfiles

    ####################################################################################################
    # Parte del anterior trabajo
    ####################################################################################################

    # Visualizaciones para análisis de clusters a través de tres graficos que relacionan clusters con cursadas promocionadas finales aprobados, y deserción

    # Distribución de cursadas promocionadas
    fig_promocionadas, ax_promocionadas = plt.subplots()
    sns.boxplot(
        data=alumnos_s_avanzados,
        x="cursadas_promocionadas",
        y="cluster",
        hue="cluster",
        legend=False,
        ax=ax_promocionadas,
    )
    ax_promocionadas.set_title("Distribución de cursadas promocionadas por cluster")

    # Distribución de finales aprobados
    fig_finales, ax_finales = plt.subplots()
    sns.boxplot(
        data=alumnos_s_avanzados,
        x="finales_aprobados",
        y="cluster",
        hue="cluster",
        legend=False,
        ax=ax_finales,
    )
    ax_finales.set_title("Distribución de finales aprobados por cluster")

    # Distribución de deserción por grupo
    _generador_aleatorio = np.random.default_rng(1)
    fig_desercion, ax_desercion = plt.subplots()
    for posicion_cluster, k in enumerate(
        sorted(alumnos_s_avanzados["cluster"].unique())
    ):
        datos_cluster = alumnos_s_avanzados[
            alumnos_s_avanzados["cluster"].astype(int) == k
        ]
        ax_desercion.scatter(
            datos_cluster["deserto"]
            + _generador_aleatorio.uniform(-0.15, 0.15, len(datos_cluster)),
            posicion_cluster
            + _generador_aleatorio.uniform(-0.25, 0.25, len(datos_cluster)),
            alpha=0.75,
            label=str(k),
        )
    ax_desercion.set_xticks([0, 1])
    ax_desercion.set_yticks(
        range(len(alumnos_s_avanzados["cluster"].cat.categories)),
        alumnos_s_avanzados["cluster"].cat.categories,
    )
    ax_desercion.set_title("Distribución de desertores por cluster")
    fig_desercion.text(
        0.5,
        0.01,
        "En desertó, 1 quiere decir que se desertó, 0 que no ",
        ha="center",
    )

    # Avance vs. promocionadas y deserción
    fig_avance, ax_avance = plt.subplots()
    for valor_deserto in sorted(alumnos_s_avanzados["deserto"].unique()):
        datos_desercion = alumnos_s_avanzados[
            alumnos_s_avanzados["deserto"] == valor_deserto
        ]
        ax_avance.scatter(
            datos_desercion["cursadas_promocionadas"]
            + _generador_aleatorio.uniform(-0.3, 0.3, len(datos_desercion)),
            datos_desercion["porc_finales"]
            + _generador_aleatorio.uniform(-0.05, 0.05, len(datos_desercion)),
            alpha=0.8,
            label=str(valor_deserto),
        )
    ax_avance.set_title(
        "Distribución de desertores por cursadas promocionadas y avance de carrera",
        fontsize=12,
    )
    ax_avance.set_ylabel("Avance de carrera")
    ax_avance.set_xlabel("Cursadas promocionadas")
    ax_avance.legend(title="Deserto")
    fig_avance.text(
        0.5,
        0.01,
        "En desertó, 1 quiere decir que se desertó, 0 que no ",
        ha="center",
    )

    # Reservar espacio para que los textos explicativos no se superpongan al eje.
    fig_desercion.subplots_adjust(bottom=0.22)
    fig_avance.subplots_adjust(bottom=0.22)

    _guardar_grafico(fig_promocionadas, "cursadas_promocionadas_por_cluster")
    _guardar_grafico(fig_finales, "finales_aprobados_por_cluster")
    _guardar_grafico(fig_desercion, "desercion_por_cluster")
    _guardar_grafico(fig_avance, "avance_vs_promocionadas")

    plt.close("all")
    print(f"Gráficos PNG guardados en: {_directorio_graficos.resolve()}")
    print(f"Dendrogramas PDF guardados en: {Path('output/dendrogramas').resolve()}")

    return {
        "ids_alumnos": ids_alumnos,
        "fecha_analisis": datos["fecha_analisis"],
        "alumnos_s_avanzados": alumnos_s_avanzados,
        "alumnos_s_avanzados_sc": alumnos_s_avanzados_sc,
        "alumnos_s_avanzados_dist_mat": alumnos_s_avanzados_dist_mat,
    }


if __name__ == "__main__":
    main()
