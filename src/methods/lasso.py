"""LASSO logistic regression from the original analysis."""

import numpy as np
import pandas as pd
from glmnet import LogitNet
from numpy.typing import ArrayLike, NDArray
from sklearn.model_selection import KFold

from src.data.constants import Columns
from src.methods.schemas import LassoResult


def analyze(eligible_students: pd.DataFrame) -> LassoResult:
    """Fit the model and display its coefficients in original units."""
    # LASSO logistic regression
    # Prepare feature and target matrices.
    X = eligible_students.drop(columns=[Columns.DROPPED_OUT])
    y = eligible_students[Columns.DROPPED_OUT]

    def _glmnet_deviance_score(
        model: LogitNet, features: ArrayLike, target: ArrayLike, lamb: ArrayLike
    ) -> NDArray[np.float64]:
        "Score binomial deviance using R glmnet's probability bounds."
        probabilities = model.predict_proba(features, lamb=lamb)[:, 1, :]
        probabilities = np.clip(probabilities, 1e-5, 1 - 1e-5)
        target = np.asarray(target).reshape(-1, 1)
        return 2 * np.mean(
            target * np.log(probabilities) + (1 - target) * np.log1p(-probabilities),
            axis=0,
        )

    np.random.seed(1)
    # LASSO model
    # Random unstratified folds, matching cv.glmnet in R.
    lasso_folds = KFold(n_splits=10, shuffle=True, random_state=1)
    lasso_groups = np.empty(len(X), dtype=int)
    for fold_number, (_, validation_indices) in enumerate(lasso_folds.split(X)):
        lasso_groups[validation_indices] = fold_number

    # glmnet standardizes internally and returns original-scale coefficients.
    # cv.glmnet clips probabilities to [1e-5, 1-1e-5] for deviance.
    # cut_point=0 selects minimum error, matching the original lambda.min.
    lasso_model = LogitNet(
        alpha=1,
        n_lambda=100,
        min_lambda_ratio=0.01 if X.shape[0] < X.shape[1] else 0.0001,
        n_splits=10,
        scoring=_glmnet_deviance_score,
        cut_point=0,
        standardize=True,
        fit_intercept=True,
        random_state=1,
    ).fit(X, y, groups=lasso_groups)

    lasso_coefficients = pd.Series(
        lasso_model.coef_[0],
        index=X.columns,
        name="coeficiente",
    )
    lasso_intercept = float(lasso_model.intercept_)
    lasso_coefficients = pd.concat(
        [
            pd.Series({"(Intercept)": lasso_intercept}, name="coeficiente"),
            lasso_coefficients,
        ]
    )
    print(lasso_coefficients)

    return {"model": lasso_model, "coefficients": lasso_coefficients}
