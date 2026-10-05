# Flujo actual a nivel de archivos

`main.py` coordina las llamadas y pasa los datos en memoria. Las ramas del diagrama representan el recorrido de los datos: los algoritmos se ejecutan en secuencia.

```mermaid
flowchart TD
    MAIN["main.py · main<br/>Fecha y parámetros"] --> MAN["data/manipulacion.py<br/>Lectura, filtros e indicadores"]
    CSV["data/*.csv"] --> MAN
    MAN --> PRE["data/preparacion.py<br/>IDs, valores originales y matriz estandarizada"]
    PRE --> EJ["main.py · ejecutar<br/>Una misma entrada para los tres métodos"]
    EJ --> J["clustering/jerarquico.py<br/>Ward, Silhouette y resumen"]
    EJ --> K["clustering/kmeans.py<br/>K-Means, Silhouette y resumen"]
    EJ --> D["clustering/dbscan.py<br/>Parámetros explícitos, ruido, Silhouette y vecinos"]
    J --> RES["Resultados en memoria"]
    K --> RES
    D --> RES
    RES --> CONSOLA["main.py<br/>Parámetros y resultados básicos en consola"]
    RES --> VIS["visualizacion.py<br/>Gráficos de los resultados"]
    PRE -. "Entrada preparada" .-> VIS
    VIS --> JPNG["output/jerarquico/graficos/<br/>PNG"]
    VIS --> KPNG["output/k-means/graficos/<br/>PNG"]
    VIS --> DPNG["output/dbscan/graficos/<br/>PNG"]
```

Cada algoritmo calcula sus etiquetas y resultados básicos: cantidad y medias por grupo, Silhouette individual y promedio. DBSCAN excluye ruido de Silhouette y registra el motivo si no se puede calcular; también devuelve las distancias de vecindad para su gráfico.

`visualizacion.py` genera figuras de tamaños, Silhouette, perfiles, distancias a vecinos y dendrogramas. Los resúmenes y resultados numéricos se muestran en consola y permanecen en memoria. No se generan CSV ni JSON.

La selección de parámetros de DBSCAN es explícita. La ejecución inicial utiliza `eps=1.5` y `min_samples=5`. No hay selección automática, comparación por ARI, tablas de correspondencia ni análisis de estabilidad en este flujo. Los módulos `evaluacion.py` y `exportacion.py` fueron retirados.

LASSO permanece como antecedente independiente.
