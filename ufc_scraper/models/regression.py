import pandas as pd
import numpy as np
import statsmodels.api as sm


class RegressionModel:
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str) -> None:
        self.df = df
        self.x_col = x_col
        self.y_col = y_col
        self.model = self._fit_model()

    def _fit_model(self):
        fitted_model = sm.OLS(
            self.df[self.y_col], sm.add_constant(self.df[self.x_col])
        ).fit()

        return fitted_model

    def check_assumptions(self):
        if r_squared_adj := self.model.rsquaredadj < 0.3:
            print(
                f"R-squared adjusted is {r_squared_adj} which is less than 0.3. This means that the model does not explain the data well."
            )
        else:
            print(f"R-squared adjusted is {r_squared_adj} which is greater than 0.3.")

    def predict(self, input_stat: float):
        #! Need refresher on what to set the constant to.
        constant: int = 0
        # input requires both the constant and the x value.
        x_test = np.array([constant, input_stat])
        # first value in returned array is the prediction (mean value in the CI).
        return self.model.get_prediction(x_test).predicted[0]
