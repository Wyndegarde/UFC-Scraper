from typing import List, DefaultDict
import numpy as np
import pandas as pd

import statsmodels.api as sm

from ufc_scraper.base_classes import DataFrameABC
from ufc_scraper.models import RegressionModel
from .fighter import Fighter

"""

RETURN TO THIS - I changed too much in previous steps to just refactor. 


High level overview of the FeatureEngineeringProcessor class:
1. Have a cleaned dataframe with all the fights in it.
2. Get a list of all unique the fighters in the dataframe.
3. We have a list of relevant columns that we want to build regression models for.
    - Purpose is to create columns that can be used to predict future events.
    - Columns are the average statistics for a fighter *going into* the respective fight
4. To do so each column is selected, then 
"""


class FeatureEngineeringProcessor(DataFrameABC):
    def __init__(self, csv_path, allow_creation) -> None:
        super().__init__(csv_path, allow_creation)
        # Returns a list of all unique fighters in the dataframe
        self.fighters = np.unique(
            np.concatenate(
                [self.object_df["red_fighter"], self.object_df["blue_fighter"]],
                axis=None,
            )
        )
        self.percent_stats = self._get_percent_stats()

    def _get_percent_stats(self) -> List[str]:
        """
        Method to extract the stats that are percentages (e.g. % of strikes landed).
        These are the stats that will be relevant for predictions
        but also required to build the models for filling missing values.

        Returns:
            List[str]: List of the column names which hold the percentage stat data.
        """

        # It's easier to work with if we remove the red_ and blue_ prefixes
        percent_stats: List[str] = [
            column.replace("red_", "").replace("blue_", "")
            for column in self.object_df.columns
            if "percent" in column
        ]
        # Quick way to drop the duplicates - changes the order tho but not important here
        return list(set(percent_stats))

    def _build_regression_df(self) -> pd.DataFrame:
        """
        Builds a dataframe that will be used to create the regression models.
        Using the relevant stats, each stat will contain an X and Y column variant.
        The X column will correspond to the average for that stat *before* a given fight.
        The Y column will correspond to the average for that stat *after* a given fight.
        So uses the overall average of the first x fights to predict the average of the first x+1 fights.

        Returns:
            pd.DataFrame: DF containing the X & Y columns for each stat.
        """
        # DF to hold all the X and Y columns for each stat
        regression_df = pd.DataFrame()
        for fighter_name in self.fighters:
            # Fighter object creates a version of the final dataframe for a single fighter.
            fighter: Fighter = Fighter(self.object_df, fighter_name)

            # Can only create a fighters regression df if they have had at least 3 fights.
            if len(fighter.fighter_df) >= 3:
                # Gets the fighters stats in chronological order (as a fighter can be in both the red and blue corner)
                ordered_stats: DefaultDict[
                    str, List[float]
                ] = fighter.order_fighter_stats(self.percent_stats)

                # Manipulate the ordered stats to create the X and Y columns for each stat.
                fighter_lin_reg_df = fighter.create_fighter_reg_df(ordered_stats)

                # Add the fighters X and Y columns to the overall regression df.
                regression_df = pd.concat([regression_df, fighter_lin_reg_df], axis=0)

        # return the final dataframe with reset index (so index 1 corresponds to row 1, not the row index of input df)
        return regression_df.reset_index(drop=True)

    def _fit_models(self):
        XYs_only = self._build_regression_df()
        # print(XYs_only.columns)
        sig_strike_model = RegressionModel(
            XYs_only, "X_sig_str_percent", "Y_sig_str_percent"
        )
        takedowns_model = RegressionModel(XYs_only, "X_td_percent", "Y_td_percent")
        sig_strike_defence_model = RegressionModel(
            XYs_only, "X_sig_strike_defence_percent", "Y_sig_strike_defence_percent"
        )
        takedowns_defence_model = RegressionModel(
            XYs_only, "X_td_defence_percent", "Y_td_defence_percent"
        )

        models = {
            "sig_strike": sig_strike_model,
            "takedowns": takedowns_model,
            "sig_strike_defence": sig_strike_defence_model,
            "takedowns_defence": takedowns_defence_model,
        }

        return models
        # return sig_strike_model

    def migration_placeholder(self):
        models = self._fit_models()

        for fighter_name in self.fighters:
            # Gets each fighter and orders their fights, earliest to most recent.
            fighter = Fighter(self.object_df, fighter_name)

            if len(fighter.fighter_df) > 1:
                all_stats = fighter.order_fighter_stats(self.percent_stats)
                df: pd.DataFrame = fighter.setup_missing_val_df(all_stats)
                sig_strike_pred = models["sig_strike"].predict(
                    df.loc[df.index[1], "sig_str_average"]
                )
                # return sig_strike_pred
                takedowns_pred = models["takedowns"].predict(
                    df.loc[df.index[1], "td_average"]
                )
                sig_strike_defence_pred = models["sig_strike_defence"].predict(
                    df.loc[df.index[1], "sig_strike_defence_average"]
                )
                takedowns_defence_pred = models["takedowns_defence"].predict(
                    df.loc[df.index[1], "td_defence_average"]
                )

                df.loc[df.index[0], "sig_str_average"] = sig_strike_pred
                df.loc[df.index[0], "td_average"] = takedowns_pred
                df.loc[
                    df.index[0], "sig_strike_defence_average"
                ] = sig_strike_defence_pred
                df.loc[df.index[0], "td_defence_average"] = takedowns_defence_pred
                # print(self.percent_stats)
                # print(df.head())


                df = df.drop(columns=self.percent_stats, axis = 1)

                for column in df.columns:
                    for i in df.index:
                        if fighter_name in self.object_df.loc[i, "red_fighter"]:
                            self.object_df.loc[i, "red_" + column] = df.loc[i, column]
                        elif fighter_name in self.object_df.loc[i, "blue_fighter"]:
                            self.object_df.loc[i, "blue_" + column] = df.loc[i, column]
        return self.object_df.head()
   
