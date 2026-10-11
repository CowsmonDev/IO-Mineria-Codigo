# Flujo actual a nivel de archivos

`main.py` procesa los argumentos de consola y delega en `src/runs/comparacion.py`. La coordinación solicita la entrada a `preparacion.py`, que carga los datos mediante `manipulacion.py`. Luego coordina las funciones `pruebas` de `runs/jerarquico.py`, `runs/kmeans.py` y `runs/dbscan.py`, pasando la misma entrada en memoria. Cada run llama a su método, genera sus gráficos y muestra sus resultados en consola. Los runs se ejecutan en secuencia. `src/methods/` contiene los cálculos; `src/runs/` contiene las ejecuciones, los casos experimentales y la exportación CSV.

El flujo permite estudiar cómo cambia el agrupamiento al cambiar de método: cada algoritmo recibe la misma matriz de alumnos y atributos. K-Means y DBSCAN no reciben las etiquetas jerárquicas como entrada.

```mermaid
flowchart TD
    MAIN["main.py · argumentos"] --> COMP["runs/comparacion.py · main"]
    COMP --> PRE["data/preparacion.py · preparar_entrada y validar_entrada"]
    CSV["data/*.csv"] --> MAN["data/manipulacion.py"] --> PRE
    ESQ["data/esquemas.py · validación Pandera"] -.-> PRE
    PRE -- "Misma entrada" --> J["runs/jerarquico.py · pruebas"]
    PRE -- "Misma entrada" --> K["runs/kmeans.py · pruebas"]
    PRE -- "Misma entrada" --> D["runs/dbscan.py · pruebas"]
    J --> MJ["methods/jerarquico.py · analizar"]
    K --> MK["methods/kmeans.py · analizar"]
    D --> MD["methods/dbscan.py · analizar"]
    J --> VIS["runs/visualizacion/visualizacion.py · generar_graficos_metodos"]
    K --> VIS
    D --> VIS
    D --> VP["runs/visualizacion/visualizacion.py · generar_graficos_experimentos_dbscan"]
    J --> CSVJ["output/jerarquico/resumen_clusters.csv"]
    VIS --> DIB["visualizacion/ · barras, perfiles, Silhouette, líneas, dendrogramas y dispersión"]
    VP --> DIB
    DIB --> GUARD["visualizacion/guardado.py · guardar_figura"]
    GUARD --> G["output/<método>/graficos/"]
    GUARD --> EXP["output/dbscan/experimentos/"]
    J -- "Resultado y casos" --> RES["comparacion.py · retorno en memoria"]
    K --> RES
    D --> RES
    L["runs/lasso.py · main"] --> PRE
    PRE -- "Valores originales" --> ML["methods/lasso.py · analizar"]
```

## Entrada común y output que cambia

La preparación conserva IDs y valores originales y produce una matriz estandarizada con diez atributos. La identidad se mantiene por posición en ambas tablas y el vector de IDs. Las etiquetas de clustering quedan fuera de los atributos.

Cada algoritmo calcula una etiqueta por alumno. Al cambiar las asignaciones cambian los tamaños, medias, distribuciones y Silhouette de los grupos. Las etiquetas numéricas son independientes entre métodos. DBSCAN puede producir otra cantidad de grupos y usa `-1` para ruido; lo excluye de Silhouette y registra el motivo cuando no se puede calcular.

Los métodos también devuelven información propia: el enlace y diagnóstico de k del jerárquico, los centros e inercia de K-Means y las distancias de vecindad y cantidad de ruido de DBSCAN.

## Salidas implementadas

Cada run llama a `src.runs.visualizacion.visualizacion.generar_graficos_metodos` con su propio resultado. La función acepta uno o varios métodos y sólo dibuja los diagnósticos jerárquicos cuando recibe ese resultado. `runs/visualizacion/visualizacion.py` arma los conjuntos de salida. Los módulos de barras, Silhouette, perfiles, líneas, dendrogramas y dispersión devuelven figuras; `guardado.py` centraliza su exportación a PNG/PDF y cierre. `generar_graficos_ejecucion` reúne los gráficos comunes de una configuración y `generar_diagnosticos_jerarquicos` agrega los diagnósticos de ese método. Los resúmenes y resultados numéricos se muestran en consola y permanecen en memoria. El jerárquico guarda además el resumen CSV original y los dendrogramas internos y zooms en PDF. No se exportan tablas comparativas ni JSON.

## Comparación pendiente

La selección de parámetros de DBSCAN es explícita. La ejecución inicial utiliza `eps=1.5` y `min_samples=5`. `src/runs/comparacion.py` delega en `src.runs.dbscan.pruebas`, que ejecuta la configuración individual y los cinco casos fijos sobre la misma entrada, imprime sus perfiles y comparación, y llama a `src.runs.visualizacion.visualizacion.generar_graficos_experimentos_dbscan` para guardar figuras en `output/dbscan/experimentos/<caso>/graficos/` y una comparación conjunta. El run devuelve `resultado` y `casos`; la coordinación conserva estos últimos como `pruebas_dbscan` en su retorno. Si la configuración individual coincide con un caso fijo, se reutiliza su resultado. Los parámetros CLI modifican solo la ejecución individual. El flujo no incluye tablas de correspondencia, ARI ni repeticiones de sensibilidad. La comparación prevista cruzará asignaciones y describirá qué perfiles se conservan, se dividen, se fusionan o quedan como ruido.

El jerárquico Python se acepta como equivalente al R sobre las entradas verificadas. La reconstrucción de la publicación no es un requisito; ver [criterios del trabajo](../criterios-del-trabajo.md#equivalencia-rpython-y-referencia-de-trabajo).

LASSO permanece como antecedente independiente y toma los valores originales. No aporta etiquetas ni pesos a los algoritmos de clustering.
