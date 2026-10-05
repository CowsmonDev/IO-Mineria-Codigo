"""Compara K-Means con la referencia jerárquica sobre la misma entrada."""

import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_samples

SEMILLAS = (123, 0, 1, 2, 3, 4, 5, 6, 7, 8)
PARAMETROS = {
    "n_clusters": 7,
    "init": "k-means++",
    "n_init": 25,
    "algorithm": "lloyd",
    "max_iter": 300,
    "tol": 1e-4,
}


def _validar(datos):
    originales = datos["alumnos_s_avanzados"]
    matriz = datos["alumnos_s_avanzados_sc"]
    ids = np.asarray(datos["ids_alumnos"])
    variables = list(matriz.columns)
    if any(nombre.startswith("cluster") for nombre in variables):
        raise ValueError("Las etiquetas de clustering no pueden integrar la entrada.")
    if variables != list(originales.drop(columns="cluster").columns):
        raise ValueError("Las variables originales y estandarizadas no coinciden.")
    if len(originales) != len(matriz) or len(ids) != len(matriz):
        raise ValueError("Las tablas y los identificadores deben tener igual longitud.")
    if pd.isna(ids).any() or pd.Series(ids).duplicated().any():
        raise ValueError("Cada fila debe tener un id_alumno único y no nulo.")
    x = matriz.to_numpy(dtype=float, copy=True)
    if not np.isfinite(x).all():
        raise ValueError("La entrada contiene valores faltantes o no finitos.")
    # Los índices difieren en la preparación original; verificar el orden por valores.
    esperada = originales[variables]
    esperada = (esperada - esperada.mean()) / esperada.std(ddof=1)
    if not np.allclose(x, esperada.to_numpy(), rtol=1e-10, atol=1e-10):
        raise ValueError(
            "La entrada no conserva el orden y la estandarización original."
        )
    etiquetas = originales["cluster"].astype(int).to_numpy()
    if len(np.unique(etiquetas)) != 7:
        raise ValueError("Se requieren los siete grupos de la referencia verificada.")
    if len(x) <= 7 or len(np.unique(x, axis=0)) < 7:
        raise ValueError(
            "No hay suficientes observaciones distintas para siete grupos."
        )
    return originales, variables, ids, x, etiquetas


def analizar(datos, *, directorio=None, directorio_graficos=None):
    """Exporta comparación y estabilidad; la ejecución presentada usa semilla 123.

    Recibe el diccionario del análisis preliminar sin modificarlo. Las repeticiones
    conservan k y todos los parámetros y cambian únicamente random_state.
    """
    originales, variables, ids, x, jerarquico = _validar(datos)
    raiz = Path(__file__).resolve().parents[2]
    salida = Path(directorio) if directorio is not None else raiz / "output/kmeans"
    graficos = (
        Path(directorio_graficos)
        if directorio_graficos is not None
        else raiz / "output/graficos/kmeans"
    )
    salida.mkdir(parents=True, exist_ok=True)
    graficos.mkdir(parents=True, exist_ok=True)
    plt.switch_backend("Agg")

    modelos = [KMeans(**PARAMETROS, random_state=s).fit(x) for s in SEMILLAS]
    principal = modelos[0]
    etiquetas = principal.labels_ + 1
    sil_h = silhouette_samples(x, jerarquico, metric="euclidean")
    sil_k = silhouette_samples(x, etiquetas, metric="euclidean")
    ari = adjusted_rand_score(jerarquico, etiquetas)
    asignaciones = pd.DataFrame(
        {
            "fila_entrada": np.arange(1, len(x) + 1),
            "id_alumno": ids,
            "cluster_jerarquico": jerarquico,
            "cluster_kmeans": etiquetas,
            "silhouette_jerarquico": sil_h,
            "silhouette_kmeans": sil_k,
        }
    )

    perfiles = []
    tamanos = []
    for metodo, grupos in (("jerarquico", jerarquico), ("kmeans", etiquetas)):
        tabla = originales[variables].reset_index(drop=True).copy()
        tabla["grupo"] = grupos
        agrupada = tabla.groupby("grupo")
        perfil = agrupada[variables].agg(["mean", "median", "std"])
        perfil.columns = [
            f"{variable}_{estadistico}" for variable, estadistico in perfil.columns
        ]
        perfil.insert(0, "cantidad", agrupada.size())
        perfil.insert(1, "proporcion", agrupada.size() / len(x))
        perfil.insert(0, "metodo", metodo)
        perfiles.append(perfil.reset_index())
        tamano = agrupada.size().rename("cantidad").reset_index()
        tamano["proporcion"] = tamano["cantidad"] / len(x)
        tamano.insert(0, "metodo", metodo)
        tamanos.append(tamano)
    perfiles = pd.concat(perfiles, ignore_index=True)
    tamanos = pd.concat(tamanos, ignore_index=True)
    correspondencia = pd.crosstab(
        asignaciones["cluster_jerarquico"], asignaciones["cluster_kmeans"]
    )
    proporciones = correspondencia.div(correspondencia.sum(axis=1), axis=0)
    metricas = pd.DataFrame(
        [
            {
                "metodo": "jerarquico",
                "grupos": 7,
                "estudiantes": len(x),
                "silhouette": sil_h.mean(),
                "inercia": None,
                "ari_con_jerarquico": 1.0,
            },
            {
                "metodo": "kmeans",
                "grupos": len(np.unique(etiquetas)),
                "estudiantes": len(x),
                "silhouette": sil_k.mean(),
                "inercia": principal.inertia_,
                "ari_con_jerarquico": ari,
            },
        ]
    )
    estabilidad = pd.DataFrame(
        [
            {
                "semilla": semilla,
                "inercia": modelo.inertia_,
                "iteraciones": modelo.n_iter_,
                "silhouette": sil_k.mean()
                if i == 0
                else silhouette_samples(x, modelo.labels_).mean(),
                "ari_con_principal": adjusted_rand_score(etiquetas, modelo.labels_),
                "ari_con_jerarquico": adjusted_rand_score(jerarquico, modelo.labels_),
                "alcanzo_max_iter": bool(modelo.n_iter_ >= PARAMETROS["max_iter"]),
            }
            for i, (semilla, modelo) in enumerate(zip(SEMILLAS, modelos))
        ]
    )
    estabilidad_asignaciones = pd.DataFrame(
        {"fila_entrada": np.arange(1, len(x) + 1), "id_alumno": ids}
    )
    for semilla, modelo in zip(SEMILLAS, modelos):
        estabilidad_asignaciones[f"semilla_{semilla}"] = modelo.labels_ + 1
    ari_semillas = pd.DataFrame(
        [[adjusted_rand_score(a.labels_, b.labels_) for b in modelos] for a in modelos],
        index=SEMILLAS,
        columns=SEMILLAS,
    ).rename_axis("semilla")
    centros = pd.DataFrame(principal.cluster_centers_, columns=variables)
    centros.index = pd.Index(range(1, 8), name="grupo")

    tablas = {
        "asignaciones": asignaciones,
        "perfiles": perfiles,
        "tamanos": tamanos,
        "metricas": metricas,
        "estabilidad": estabilidad,
        "asignaciones_estabilidad": estabilidad_asignaciones,
    }
    for nombre, tabla in tablas.items():
        tabla.to_csv(salida / f"{nombre}.csv", index=False)
    for nombre, tabla in {
        "correspondencia": correspondencia,
        "correspondencia_proporciones": proporciones,
        "ari_entre_semillas": ari_semillas,
        "centros_estandarizados": centros,
    }.items():
        tabla.to_csv(salida / f"{nombre}.csv")

    huella = hashlib.sha256()
    huella.update(json.dumps(variables, ensure_ascii=False).encode())
    huella.update(
        pd.util.hash_pandas_object(pd.Series(ids), index=False).values.tobytes()
    )
    huella.update(np.ascontiguousarray(x, dtype="<f8").tobytes())
    configuracion = {
        "fecha_analisis": datos["fecha_analisis"],
        "estudiantes": len(x),
        "variables": variables,
        "incluye_deserto": "deserto" in variables,
        "estandarizacion": "media y desvio muestral (ddof=1)",
        "entrada_sha256": huella.hexdigest(),
        "referencia_sha256": hashlib.sha256(
            jerarquico.astype("<i8").tobytes()
        ).hexdigest(),
        "parametros": PARAMETROS,
        "semilla_principal": SEMILLAS[0],
        "semillas_estabilidad": SEMILLAS,
        "seleccion": "Semilla 123 prefijada; menor inercia entre sus 25 inicializaciones.",
        "versiones": {
            nombre: version(nombre)
            for nombre in (
                "scikit-learn",
                "numpy",
                "pandas",
                "scipy",
                "matplotlib",
                "seaborn",
            )
        },
        "interpretacion": "ARI mide concordancia, no calidad. deserto integra la entrada: su perfil no es validacion independiente.",
    }
    (salida / "configuracion.json").write_text(
        json.dumps(configuracion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    def guardar(fig, nombre):
        fig.savefig(graficos / f"{nombre}.png", dpi=160, bbox_inches="tight")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(correspondencia, annot=True, fmt="d", cmap="Blues", ax=ax)
    ax.set(
        title="Correspondencia de estudiantes",
        xlabel="Grupo K-Means",
        ylabel="Grupo jerárquico",
    )
    guardar(fig, "correspondencia")
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(
        proporciones, annot=True, fmt=".1%", vmin=0, vmax=1, cmap="Blues", ax=ax
    )
    ax.set(
        title="Distribución de cada grupo jerárquico",
        xlabel="Grupo K-Means",
        ylabel="Grupo jerárquico",
    )
    guardar(fig, "correspondencia_proporciones")
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=tamanos, x="grupo", y="cantidad", hue="metodo", ax=ax)
    ax.set(
        title="Tamaños de grupos (las etiquetas no implican correspondencia)",
        xlabel="Grupo",
        ylabel="Estudiantes",
    )
    guardar(fig, "tamanos")
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharex=True)
    for ax, nombre, grupos, valores in zip(
        axes, ("Jerárquico", "K-Means"), (jerarquico, etiquetas), (sil_h, sil_k)
    ):
        inicio = 0
        for grupo in np.unique(grupos):
            ordenados = np.sort(valores[grupos == grupo])
            ax.fill_betweenx(np.arange(inicio, inicio + len(ordenados)), 0, ordenados)
            ax.text(-0.95, inicio + len(ordenados) / 2, str(grupo))
            inicio += len(ordenados) + 10
        ax.axvline(valores.mean(), color="red", linestyle="--")
        ax.set(
            title=f"{nombre}: {valores.mean():.4f}",
            xlabel="Silhouette",
            ylabel="Grupo",
            xlim=(-1, 1),
            yticks=[],
        )
    guardar(fig, "silhouette")
    fig, axes = plt.subplots(1, 2, figsize=(max(14, len(variables) * 1.2), 6))
    for ax, nombre, grupos in zip(
        axes, ("Jerárquico", "K-Means"), (jerarquico, etiquetas)
    ):
        medias = (
            pd.DataFrame(x, columns=variables)
            .assign(grupo=grupos)
            .groupby("grupo")
            .mean()
        )
        sns.heatmap(medias, center=0, vmin=-3, vmax=3, cmap="vlag", ax=ax)
        ax.set(title=f"Perfiles {nombre} (medias estandarizadas)", ylabel="Grupo")
    guardar(fig, "perfiles")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        ari_semillas, vmin=0, vmax=1, annot=True, fmt=".3f", cmap="Blues", ax=ax
    )
    ax.set(
        title="Estabilidad K-Means: ARI entre semillas",
        xlabel="Semilla",
        ylabel="Semilla",
    )
    guardar(fig, "estabilidad")

    print(metricas.to_string(index=False))
    print(
        f"Estabilidad: ARI mínimo entre semillas = {ari_semillas.to_numpy()[np.triu_indices(len(SEMILLAS), k=1)].min():.4f}"
    )
    print(f"Tablas y configuración: {salida.resolve()}")
    print(f"Gráficos K-Means: {graficos.resolve()}")
    return {
        **tablas,
        "correspondencia": correspondencia,
        "configuracion": configuracion,
    }
