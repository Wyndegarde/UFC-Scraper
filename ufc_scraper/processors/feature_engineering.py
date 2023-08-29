from typing import List, Any
import numpy as np
import pandas as pd
# import statsmodels.formula.api as smf
import statsmodels.api as sm

from ufc_scraper.base_classes import DataFrameABC

"""

RETURN TO THIS - I changed too much in previous steps to just refactor. 


High level overview of the FeatureEngineeringProcessor class:
1. Have a cleaned dataframe with all the fights in it.
2. Get a list of all unique the fighters in the dataframe.
3. We have a list of relevant columns that we want to build regression models for.
    - Purpose is to create columns that can be used to predict future events.
    - These columns are the average statistics for a fighter *going into* the respective fight.
4. To do so each column is selected, then 
"""


class FeatureEngineeringProcessor(DataFrameABC):
    def __init__(self, csv_path, allow_creation) -> None:
        super().__init__(csv_path, allow_creation)
        self.fighters = np.unique(
            np.concatenate(
                [self.object_df["red_fighter"], self.object_df["blue_fighter"]],
                axis=None,
            )
        )
        self.percent_stats = [
            column.replace("red_", "").replace("blue_", "")
            for column in self.object_df.columns
            if "%" in column
        ]

    def _get_fighter_df(self, fighter_name: str) -> pd.DataFrame:
        return self.object_df[
            (self.object_df["red_fighter"] == fighter_name)
            | (self.object_df["blue_fighter"] == fighter_name)
        ].sort_values(by="date", ascending=True)

    def _populate_fighter_df(
        self, stats_col, fighter_name, fighter_df: pd.DataFrame
    ) -> List[Any]:
        ordered_stats = []

        for i in fighter_df.index:
            if fighter_name in fighter_df.loc[i, "red_fighter"]:
                ordered_stats.append(fighter_df.loc[i, "red_" + stats_col])
            if fighter_name in fighter_df.loc[i, "blue_fighter"]:
                ordered_stats.append(fighter_df.loc[i, "blue_" + stats_col])

        return ordered_stats

    def _populate_reg_df(self, ordered_stats, each_stat_df, stats_col):
        lin_reg_df = pd.DataFrame(ordered_stats, columns=[stats_col])
        lin_reg_df["X_" + stats_col] = (
            lin_reg_df[stats_col].expanding(2).mean().shift(1)
        )
        lin_reg_df.loc[1, "X_" + stats_col] = lin_reg_df.loc[0, stats_col]
        lin_reg_df["Y_" + stats_col] = lin_reg_df["X_" + stats_col].shift(1)
        lin_reg_df = lin_reg_df.dropna()

        each_stat_df = pd.concat(
            [each_stat_df, lin_reg_df], axis=0
        )  # Adds the rows of each fighter to the dataframe for that stat.
        return each_stat_df

    def _build_regression_df(self) -> pd.DataFrame:
        regression_df = pd.DataFrame()
        for column in self.percent_stats:
            each_stat_df = pd.DataFrame(
                columns=[column, "Y_" + column, "X_" + column]
            )  # Builds a dataframe for each stat.
            for fighter in self.fighters:
                fighter_df = self._get_fighter_df(fighter)

                if len(fighter_df) >= 3:
                    ordered_stats = self._populate_fighter_df(
                        column, fighter, fighter_df
                    )
                    each_stat_df = self._populate_reg_df(
                        ordered_stats, each_stat_df, column
                    )
            regression_df = pd.concat([regression_df, each_stat_df], axis=1)
        regression_df = regression_df.reset_index(drop=True)

        XYs_only = regression_df.drop(self.percent_stats, axis=1)

        return XYs_only

    def _fit_models(self):
        XYs_only = self._build_regression_df()
        # print(XYs_only.columns)
        print(self.object_df.columns)

        sig_strike_model = sm.OLS(
            XYs_only["Y_sig_str_%"], sm.add_constant(XYs_only["X_sig_str_%"])
        ).fit()
        takedowns_model = sm.OLS(
            XYs_only["Y_td_%"], sm.add_constant(XYs_only["X_td_%"])
        ).fit()
        sig_strike_defence_model = sm.OLS(
            XYs_only["Y_sig_str_def_%"], sm.add_constant(XYs_only["X_sig_str_def_%"])
        ).fit()
        takedowns_defence_model = sm.OLS(
            XYs_only["Y_td_def_%"], sm.add_constant(XYs_only["X_td_def_%"])
        ).fit()

        models = {
            "sig_strike": sig_strike_model,
            "takedowns": takedowns_model,
            "sig_strike_defence": sig_strike_defence_model,
            "takedowns_defence": takedowns_defence_model,
        }

        return models
        # return sig_strike_model

    def _create_new_col_names(self):
        red_blue_percent_stats = [
            column
            for column in self.object_df.columns
            if "percent" in column and "total" not in column
        ]

        # new_columns = []
        for name in red_blue_percent_stats:
            string = name.replace("percent", "average")
            # new_columns.append(string)
            self.object_df[string] = np.nan

    def migration_placeholder(self):
        models = self._fit_models()
        sig_strike_model = models["sig_strike"]
        takedowns_model = models["takedowns"]
        sig_strike_defence_model = models["sig_strike_defence"]
        takedowns_defence_model = models["takedowns_defence"]

        self._create_new_col_names()

        for fighter in self.fighters:
            fighter_df = self._get_fighter_df(
                self.object_df, fighter
            )  # Gets each fighter and orders their fights, earliest to most recent.

            if len(fighter_df) > 1:
                sig_strikes = []
                takedowns = []
                sig_strike_defence = []
                takedown_defence = []

                for i in fighter_df.index:
                    if fighter in fighter_df.loc[i, "red_fighter"]:
                        sig_strikes.append(fighter_df.loc[i, "red_sig_strike_percent"])
                        takedowns.append(fighter_df.loc[i, "red_takedowns_percent"])
                        sig_strike_defence.append(
                            fighter_df.loc[i, "red_sig_strike_defence_percent"]
                        )
                        takedown_defence.append(
                            fighter_df.loc[i, "red_takedowns_defence_percent"]
                        )

                    if fighter in fighter_df.loc[i, "blue_fighter"]:
                        sig_strikes.append(fighter_df.loc[i, "blue_sig_strike_percent"])
                        takedowns.append(fighter_df.loc[i, "blue_takedowns_percent"])
                        sig_strike_defence.append(
                            fighter_df.loc[i, "blue_sig_strike_defence_percent"]
                        )
                        takedown_defence.append(
                            fighter_df.loc[i, "blue_takedowns_defence_percent"]
                        )

                dic = {
                    "sig_strike": sig_strikes,
                    "takedowns": takedowns,
                    "sig_strike_defence": sig_strike_defence,
                    "takedowns_defence": takedown_defence,
                }
                df = pd.DataFrame(dic, index=fighter_df.index)

                for column in df.columns:
                    column_name = column + "_average"
                    df[column_name] = df[column].expanding(2).mean().shift(1)
                    df.loc[df.index[1], column_name] = df.loc[df.index[0], column]

                predict_sig_strikes = sig_strike_model.predict(
                    exog=dict(
                        X_sig_strike_percent=df.loc[df.index[1], "sig_strike_average"]
                    )
                )
                predict_takedowns = takedowns_model.predict(
                    exog=dict(
                        X_takedowns_percent=df.loc[df.index[1], "takedowns_average"]
                    )
                )

                predict_sig_strike_defence = sig_strike_defence_model.predict(
                    exog=dict(
                        X_sig_strike_defence_percent=df.loc[
                            df.index[1], "sig_strike_defence_average"
                        ]
                    )
                )
                predict_takedown_defence = takedowns_defence_model.predict(
                    exog=dict(
                        X_takedowns_defence_percent=df.loc[
                            df.index[1], "takedowns_defence_average"
                        ]
                    )
                )

                df.loc[df.index[0], "sig_strike_average"] = predict_sig_strikes[0]
                df.loc[df.index[0], "takedowns_average"] = predict_takedowns[0]
                df.loc[
                    df.index[0], "sig_strike_defence_average"
                ] = predict_sig_strike_defence[0]
                df.loc[
                    df.index[0], "takedowns_defence_average"
                ] = predict_takedown_defence[0]

                df = df.drop(
                    columns=[
                        "sig_strike",
                        "takedowns",
                        "sig_strike_defence",
                        "takedowns_defence",
                    ]
                )

                for column in df.columns:
                    for i in df.index:
                        if fighter in self.object_df.loc[i, "red_fighter"]:
                            self.object_df.loc[i, "red_" + column] = df.loc[i, column]
                        elif fighter in self.object_df.loc[i, "blue_fighter"]:
                            self.object_df.loc[i, "blue_" + column] = df.loc[i, column]


def create_regression_model():
    """
    Responsible for creating the regression models for each of the stats we are interested in.
    Will return a trained regression model for each of the stats. to be used to fill missing values.
    """
    ...


class AssumptionChecking:
    """
    Will hold all the methods for checking the assumptions of the regression models.
    Mainly visualisations
    """

    ...


def fill_missing_values():
    """
    Responsible for filling in the missing values of the dataframe.
    uses the trained regression models to predict the missing values.
    """
    ...


def test_filled_values():
    """
    Responsible for testing the filled values.
    """
    ...
