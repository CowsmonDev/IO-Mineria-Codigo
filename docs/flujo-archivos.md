# Flujo actual a nivel de archivos

`main.py` solicita la entrada a `preparacion.py`, que carga los datos mediante `manipulacion.py`. Luego coordina los algoritmos y pasa la entrada en memoria. Los algoritmos se ejecutan en secuencia.

```mermaid
flowchart TD
    MAIN["main.py · main<br/>Fecha y parámetros"] --> PRE["data/preparacion.py · preparar_entrada<br/>IDs, valores originales y matriz estandarizada"]
    PRE -- "Carga con fecha de análisis" --> MAN["data/manipulacion.py · preparar_datos_academicos<br/>Lectura, filtros e indicadores"]
    CSV["data/*.csv"] --> MAN
    MAN -- "Datos académicos" --> PRE
    LASSO["lasso.py · main"] -- "Solicita entrada" --> PRE
    PRE -- "originales" --> LASSOFIT["lasso.py · analizar<br/>Regresión logística LASSO"]
    PRE --> EJ["main.py<br/>Una misma entrada para los tres métodos"]
    EJ --> J["clustering/jerarquico.py<br/>Ward, Silhouette y resumen"]
    EJ --> K["clustering/kmeans.py<br/>K-Means, Silhouette y resumen"]
    EJ --> D["clustering/dbscan.py<br/>Parámetros explícitos, ruido, Silhouette y vecinos"]
    J --> RES["Resultados en memoria"]
    K --> RES
    D --> RES
    RES --> CSVJ["jerarquico.py · guardar_resumen<br/>output/jerarquico/resumen_clusters.csv"]
    RES --> CONSOLA["main.py<br/>Parámetros y resultados básicos en consola"]
    RES --> VIS["visualizacion.py<br/>Gráficos de los resultados"]
    PRE -. "Entrada preparada" .-> VIS
    VIS --> JPNG["output/jerarquico/graficos/<br/>PNG y PDF"]
    VIS --> KPNG["output/k-means/graficos/<br/>PNG"]
    VIS --> DPNG["output/dbscan/graficos/<br/>PNG"]
```

Cada algoritmo calcula sus etiquetas y resultados básicos: cantidad y medias por grupo, Silhouette individual y promedio. DBSCAN excluye ruido de Silhouette y registra el motivo si no se puede calcular; también devuelve las distancias de vecindad para su gráfico.

`visualizacion.py` genera figuras de tamaños, Silhouette, perfiles, distancias a vecinos y dendrogramas. Los resúmenes y resultados numéricos se muestran en consola y permanecen en memoria. El jerárquico guarda además el resumen CSV original y los dendrogramas internos y zooms en PDF. No se generan tablas comparativas ni JSON.

La selección de parámetros de DBSCAN es explícita. La ejecución inicial utiliza `eps=1.5` y `min_samples=5`. No hay selección automática, comparación por ARI, tablas de correspondencia ni análisis de estabilidad en este flujo. Los módulos `evaluacion.py` y `exportacion.py` fueron retirados.

LASSO permanece como antecedente independiente.
