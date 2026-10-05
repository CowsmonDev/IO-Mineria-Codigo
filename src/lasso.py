"""Regresión logística LASSO del análisis original."""

import numpy as np
import pandas as pd
from glmnet import LogitNet
from sklearn.model_selection import KFold

from src.data.preparacion import preparar_entrada


def analizar(alumnos_s_avanzados):
    """Ajusta el modelo y muestra sus coeficientes en las unidades originales."""
    # REGRESIÓN LOGÍSTICA LASSO
    # Preparar matrices
    X = alumnos_s_avanzados.drop(columns=["deserto"])
    y = alumnos_s_avanzados["deserto"]

    def _glmnet_deviance_score(model, features, target, lamb):
        """Score binomial deviance using R glmnet's probability bounds."""
        probabilities = model.predict_proba(features, lamb=lamb)[:, 1, :]
        probabilities = np.clip(probabilities, 1e-5, 1 - 1e-5)
        target = np.asarray(target).reshape(-1, 1)
        return 2 * np.mean(
            target * np.log(probabilities) + (1 - target) * np.log1p(-probabilities),
            axis=0,
        )

    np.random.seed(1)
    # Modelo LASSO
    # Particiones aleatorias sin estratificar, como cv.glmnet en R.
    particiones_lasso = KFold(n_splits=10, shuffle=True, random_state=1)
    grupos_lasso = np.empty(len(X), dtype=int)
    for numero_particion, (_, indices_validacion) in enumerate(
        particiones_lasso.split(X)
    ):
        grupos_lasso[indices_validacion] = numero_particion

    # glmnet estandariza internamente y devuelve coeficientes en la escala original.
    # cv.glmnet limita probabilidades a [1e-5, 1-1e-5] al calcular la deviance.
    # cut_point=0 selecciona el mínimo error, como s="lambda.min" en el original.
    modelo_lasso = LogitNet(
        alpha=1,
        n_lambda=100,
        min_lambda_ratio=0.01 if X.shape[0] < X.shape[1] else 0.0001,
        n_splits=10,
        scoring=_glmnet_deviance_score,
        cut_point=0,
        standardize=True,
        fit_intercept=True,
        random_state=1,
    ).fit(X, y, groups=grupos_lasso)

    coeficientes_lasso = pd.Series(
        modelo_lasso.coef_[0],
        index=X.columns,
        name="coeficiente",
    )
    intercepto_lasso = float(modelo_lasso.intercept_)
    coeficientes_lasso = pd.concat(
        [
            pd.Series({"(Intercept)": intercepto_lasso}, name="coeficiente"),
            coeficientes_lasso,
        ]
    )
    print(coeficientes_lasso)

    return {"modelo": modelo_lasso, "coeficientes": coeficientes_lasso}


def main(*, fecha_analisis=None):
    """Ejecuta el antecedente LASSO por separado de la comparación."""
    entrada = preparar_entrada(fecha_analisis=fecha_analisis)
    return analizar(entrada["originales"])


if __name__ == "__main__":
    main()
