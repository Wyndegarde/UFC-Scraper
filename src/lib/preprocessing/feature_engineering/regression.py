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

    def predict(self, input_stat: float) -> float:
        """
        Predicts the target value using the trained model.

        Args:
            input_stat: The input statistic to predict from

        Returns:
            float: The predicted value
        """
        x_test = np.array([1, input_stat])  # 1 is the constant term for statsmodels
        return self.model.get_prediction(x_test).predicted[0]
