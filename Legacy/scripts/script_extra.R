# Biblioteca para hacer K-Means y DBSCAN
library(cluster)
library(dbscan)

library(hopkins) # Borrar después, es para ver si el dataset es clusterizable

# Para chequear si es clusterizable el dataset
hopkins_stat <- hopkins(alumnos_s_avanzados_sc)
print(hopkins_stat)

# ------------------------------
# K-MEANS
# ------------------------------
set.seed(123)  # Para reproducibilidad
kmeans_model <- kmeans(alumnos_s_avanzados_sc, centers = 4, nstart = 25) #esto todavia no ejecuta, porque hay NA en dias_dsd_ult_final
alumnos_s_avanzados$cluster_kmeans <- as.factor(kmeans_model$cluster)

# ------------------------------
# DBSCAN
# ------------------------------

# Estimar parámetro eps visualmente (opcional)
kNNdistplot(alumnos_s_avanzados_sc, k = 5)
abline(h = 1.5, col = "red")  # Ajustar según curva

# Ejecutar DBSCAN
db_model <- dbscan(alumnos_s_avanzados_sc, eps = 1.5, minPts = 5)
alumnos_s_avanzados$cluster_dbscan <- as.factor(db_model$cluster)  # 0 indica outliers

# ----------------------------------
# SILHOUETTE K-MEANS, PAM Y DBSCAN
# ----------------------------------

# Silhouette para K-means
sil_k <- silhouette(as.numeric(alumnos_s_avanzados$cluster_kmeans), dist(alumnos_s_avanzados_sc))
par(mfrow = c(1,1))
plot(sil_k, main = "Silhouette - K-means", border = NA)

# Silhouette para DBSCAN (excluyendo outliers)
dbscan_valid_idx <- which(db_model$cluster != 0)
sil_d <- silhouette(db_model$cluster[dbscan_valid_idx], dist(alumnos_s_avanzados_sc[dbscan_valid_idx, ]))
par(mfrow = c(1,1))
plot(sil_d, main = "Silhouette - DBSCAN", border = NA)

# Para ver los promedios de Kmeans, PAM y DBScan
set.seed(123)
kmeans_res <- kmeans(alumnos_s_avanzados_sc, centers = 7, nstart = 25)
sil_kmeans <- silhouette(kmeans_res$cluster, dist(alumnos_s_avanzados_sc))
mean(sil_kmeans[, 3])  # promedio silhouette

pam_res <- pam(alumnos_s_avanzados_sc, k = 7)
sil_pam <- silhouette(pam_res$clustering, dist(alumnos_s_avanzados_sc))
mean(sil_pam[, 3])

db_model <- dbscan(alumnos_s_avanzados_sc, eps = 1.5, minPts = 5)
alumnos_s_avanzados$cluster_dbscan <- as.factor(db_model$cluster)
dbscan_valid_idx <- which(db_model$cluster != 0)
sil_d <- silhouette(db_model$cluster[dbscan_valid_idx], dist(alumnos_s_avanzados_sc[dbscan_valid_idx, ]))
mean(sil_d[, 3])

# RANDOM FOREST
library(randomForest)

rf_model <- randomForest(as.factor(deserto) ~ ., data = alumnos_s_avanzados, importance = TRUE)
varImpPlot(rf_model)