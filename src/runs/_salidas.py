"""Presentación en consola compartida por las ejecuciones."""


def imprimir_resultado(metodo, resultado):
    """Muestra parámetros, perfiles y disponibilidad de Silhouette."""
    print(f"\n{metodo}: {resultado['parametros']}")
    print(resultado["resumen"].to_string())
    if resultado["motivo_silhouette"]:
        print(resultado["motivo_silhouette"])
    else:
        print(
            f"Silhouette: {resultado['silhouette_promedio']:.6f} sobre {resultado['poblacion_silhouette']} estudiantes"
        )
    if "ruido" in resultado:
        print(f"Ruido: {resultado['ruido']}/{len(resultado['etiquetas'])} estudiantes")
