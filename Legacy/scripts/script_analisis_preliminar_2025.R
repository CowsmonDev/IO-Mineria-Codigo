library(lubridate)
# Biblioteca para generar el dendograma
library(dendextend)
# Biblioteca para generar los boxplot
library(ggplot2)
# Biblioteca para realizar la regresión logística LASSO
library(glmnet)

# Análisis de desertores que desaprobaron materias importantes de Ingeniería en Sistemas

alumnos_s_avanzados_desaprob_mat_IS %>%
  summarise(porc_desertores = mean(deserto == TRUE) * 100)

# Análisis de desertores que nacieron en la localidad de Tandil (donde se cursa la carrera)

alumnos_desertores %>%
  summarise(porc_desertores_fuera_tandil = mean(deserto == TRUE & !localidad_nacimiento == 'TANDIL') * 100)


# Removemos la información que no es necesario del dataframe para analizar y poner la información en el formato correcto
# Limpieza y selección de variables relevantes
# Objetivo: preparar los datos solo con las variables numéricas necesarias para hacer clustering.
alumnos_s_avanzados<- alumnos_s_avanzados %>%
  mutate(
    tiempo_desde_ingreso = as.numeric(tiempo_desde_ingreso),
    deserto = as.numeric(deserto),
    dias_dsd_ultimo_final = as.numeric(dias_dsd_ultimo_final)
  )

# Eliminamos variables que no nos interesan para el análisis

alumnos_s_avanzados <- alumnos_s_avanzados %>%
  select(-nota_finales_ult_anio,
         -cursadas_regulares,
         -notas_cursadas_ult_anio,
         -relacion_finales_cursadas, 
         -porc_cursadas,
         -total_materias_finalizadas,
         -localidad_nacimiento,
         -fecha_inscripcion,
         -cambio_plan,
         -id_alumno, 
         -plan, 
         -carrera,
         -calidad)

# REGRESIÓN LOGÍSTICA LASSO
# Preparar matrices
X <- model.matrix(deserto ~ . -1, data = alumnos_s_avanzados)  # quitar intercepto
y <- alumnos_s_avanzados$deserto

set.seed(1)
# Modelo LASSO
modelo_lasso <- cv.glmnet(X, y, family = "binomial", alpha = 1)
coef(modelo_lasso, s = "lambda.min")

# Configuracion de la semilla aleatoria: Fija la semilla para garantizar que cualquier operación aleatoria (como el dendrograma) sea reproducible.
set.seed(1)

# Muestra de una matriz de correlacion para la tabla de alumnos sin recibidos
# Creación de la matriz de correlación y normalización
# Generación del dendograma y la clusterización jerárquica
# scale(): normaliza las variables (media = 0, desvío estándar = 1).
# cor(): calcula la matriz de correlación entre variables normalizadas y no normalizadas.

matriz_cor <- as.data.frame(cor(scale(alumnos_s_avanzados)))
matriz_cor_comparacion <- as.data.frame(cor(alumnos_s_avanzados))
alumnos_s_avanzados_sc <- as.data.frame(scale(alumnos_s_avanzados))

# Creación de la matriz de distancias y clustering jerárquico
# Calcula las distancias euclideanas entre estudiantes.
# Realiza un clustering jerárquico completo (hclust).
# Corta el dendrograma a una altura h = 35 para formar los clusters.

alumnos_s_avanzados_dist_mat <- dist(alumnos_s_avanzados_sc, method =  "euclidean")
hclust_alumnos_s_avanzados <- hclust(alumnos_s_avanzados_dist_mat, method = "ward.D2") # Cambiamos complete por ward.D2
hclustered_alumnos_s_avanzados <- cutree(hclust_alumnos_s_avanzados, h = 35)

# Visualización del dendrograma
# Muestra el árbol de decisión jerárquico coloreado por grupo.
# Ayuda a visualizar cómo se formaron los clusters.

as.dendrogram(hclust_alumnos_s_avanzados) %>%
  set("branches_k_col", value =7:1, h = 35) %>%
  set("labels", rep("", length(labels(as.dendrogram(hclust_alumnos_s_avanzados))))) %>%
  plot(ylim=c(0,50))
  #plot()

# Actualización del dataframe con la información del cluster -> Asignación del cluster a cada alumno
alumnos_s_avanzados$cluster <- as.factor(hclustered_alumnos_s_avanzados)

# Creación de un resumen de los clusters -> Resumen estadístico por cluster
# Muestra cómo se comportan las variables clave en cada cluster: si son más desertores, si promocionan más materias, etc.

resumen_cluster <- alumnos_s_avanzados %>% group_by(cluster) %>%
  summarise(cantidad_observaciones = n(),
            media_cursadas_aprobadas = mean(cursadas_aprobadas),
            media_cursadas_desaprobadas = mean(cursadas_desaprobadas),
            media_materias_anotado_ult_anio = mean(materias_anotado_ult_anio),
            media_finales_aprobados = mean(finales_aprobados),
            media_finales_desaprobados = mean(finales_desaprobados),
            media_cursadas_promocionadas = mean(cursadas_promocionadas),
            media_porc_finales = mean(porc_finales),
            media_T_desde_ingreso = mean(tiempo_desde_ingreso),
            media_deserto = mean(deserto, na.rm = TRUE),
            media_dias_dsd_ultimo_final = mean(dias_dsd_ultimo_final, na.rm = TRUE)
  )

# =====================================
# NUEVO: Dendrogramas individuales por cluster
# =====================================

# Crear carpeta de salida si no existe
if (!dir.exists("output/dendrogramas")) dir.create("output/dendrogramas", recursive = TRUE)

# Asignar nombres de fila para mantener trazabilidad
rownames(alumnos_s_avanzados_sc) <- 1:nrow(alumnos_s_avanzados_sc)

# Generar dendrogramas internos y exportar como PDF
for (k in sort(unique(alumnos_s_avanzados$cluster))) {
  cat("Generando dendrograma para cluster:", k, "
")
  idx <- which(alumnos_s_avanzados$cluster == k)
  datos_cluster <- alumnos_s_avanzados_sc[idx, ]
  
  if (nrow(datos_cluster) > 2) {
    dist_cl <- dist(datos_cluster)
    hc_cl <- hclust(dist_cl, method = "ward.D2")
    dend <- as.dendrogram(hc_cl)
    
    # Cortar en 4 subgrupos internos para análisis
    subgrupos <- cutree(hc_cl, k = 4)
    
    # Guardar dendrograma completo con rectángulos por subgrupo
    pdf(file = paste0("output/dendrogramas/dendrograma_cluster_", k, ".pdf"), 
        width = 15, height = 10)
    plot(dend,
         main = paste("Dendrograma interno - Cluster", k),
         ylab = "Altura (distancia)",
         leaflab = "none",
         cex = 0.6)
    rect.hclust(hc_cl, k = 4, border = 2:5)
    dev.off()
    
    # Guardar dendrograma con zoom (primeros 50 casos si hay suficientes)
    if (nrow(datos_cluster) >= 500) {
      datos_subset <- datos_cluster[1:50, ]
      hc_subset <- hclust(dist(datos_subset), method = "ward.D2")
      dend_subset <- as.dendrogram(hc_subset)
      
      pdf(file = paste0("output/dendrogramas/dendrograma_zoom_cluster_", k, ".pdf"),
          width = 12, height = 8)
      plot(dend_subset,
           main = paste("Zoom - Cluster", k, "(Primeros 50 casos)"),
           ylab = "Altura (distancia)",
           cex = 0.7)
      rect.hclust(hc_subset, k = 3, border = 2:4)
      dev.off()
    }
  } else {
    cat("Cluster", k, "tiene muy pocos elementos para dendrograma.
")
  }
}

# Para exportar el resumen de los clusters formados por el clustering jerarquico
write.csv(resumen_cluster, "resumen_clusters.csv", row.names = FALSE)

# ------------------------------
# Validación de agrupamientos
# ------------------------------

# Silhouette para jerárquico
sil_h <- silhouette(as.numeric(alumnos_s_avanzados$cluster), dist(alumnos_s_avanzados_sc))
par(mfrow = c(1,1))
plot(sil_h, main = "Silhouette - Jerárquico", border = NA)

###########################################################
# Encontrar el mejor valor de k, usando Silhouette Score
###########################################################

sil_scores <- c()
for (k in 2:15) {
  clust_temp <- cutree(hclust_alumnos_s_avanzados, k = k)
  sil <- silhouette(clust_temp, alumnos_s_avanzados_dist_mat)
  sil_scores[k] <- mean(sil[, 3])
}

# Graficar resultados
plot(2:15, sil_scores[2:15], type = "b", pch = 19,
     xlab = "Número de clústeres (k)",
     ylab = "Silhouette promedio",
     main = "Silhouette score para cada k")



####################################################################################################
# Parte del anterior trabajo
####################################################################################################

# Visualizaciones para análisis de clusters a través de tres graficos que relacionan clusters con cursadas promocionadas finales aprobados, y deserción

# Distribución de cursadas promocionadas
ggplot(alumnos_s_avanzados, aes(x = (cursadas_promocionadas), y = cluster, group = cluster, fill = cluster)) +
  geom_boxplot() +
  labs(title = "Distribución de cursadas promocionadas por cluster")

# Distribución de finales aprobados
ggplot(alumnos_s_avanzados, aes(x = finales_aprobados, y = cluster, group = cluster, fill = cluster)) +
  geom_boxplot() +
  labs(title = "Distribución de finales aprobados por cluster")

# Distribución de deserción por grupo
ggplot(alumnos_s_avanzados, aes(x = deserto, y = cluster, colour = cluster)) +
  geom_point(position = position_jitter(width = 0.15, height = 0.25), alpha = 0.75) +
  scale_x_continuous(breaks = c(0, 1)) +
  labs(title = "Distribución de desertores por cluster") +
  labs(caption = "En desertó, 1 quiere decir que se desertó, 0 que no ")

# Avance vs. promocionadas y deserción
ggplot(alumnos_s_avanzados, aes(x = cursadas_promocionadas, y = porc_finales, colour = as.factor(deserto))) +
  geom_point(alpha = 0.8, position = position_jitter(width = 0.3, height = 0.05)) +
  labs(title = "Distribución de desertores por cursadas promocionadas y avance de carrera") +
  labs(y = "Avance de carrera", x = "Cursadas promocionadas", color = "Deserto") +
  labs(caption = "En desertó, 1 quiere decir que se desertó, 0 que no ") +
  theme(plot.title = element_text(size = 12))