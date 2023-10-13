from typing import List, DefaultDict, Any, Dict
import numpy as np
import pandas as pd

from ufc_scraper.base_classes import DataFrameABC
from ufc_scraper.config import PathSettings
from .regression import RegressionModel
from .fighter import Fighter


class FeatureEngineering(DataFrameABC):
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

    def _fit_models(self) -> Dict[str, RegressionModel]:
        """
        Method to create the linear regression models that will predict what our missing values should be.


        Returns:
            RegressionModel: Custom Class that makes it a bit easier to work with the statsmodels package.
        """
        # DF containing the X and Y columns for each stat.
        XYs_only = self._build_regression_df()

        # All the models are created here.
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
        # Store them in a dictionary for easy access.
        models = {
            "sig_strike": sig_strike_model,
            "takedowns": takedowns_model,
            "sig_strike_defence": sig_strike_defence_model,
            "takedowns_defence": takedowns_defence_model,
        }

        return models

    def _populate_averages_cols(
        self, fighter_stats_df: pd.DataFrame, fighter_name: str
    ) -> None:
        """
        Takes the dataframe containing the average stats for a given fighter
        and populates the main dataframe with the values.
        This in effect adds a new column for each stat to the main dataframe,
        where the values are the average stats for a given fighter *before* the bout in that row.

        Args:
            fighter_stats_df (pd.DataFrame): the dataframe containing the average stats for a given fighter
            fighter_name (str): The name of the fighter.
        """

        for column in fighter_stats_df.columns:
            # Because the fighter_stats_df is a subset of the main dataframe, the index is shared.
            for i in fighter_stats_df.index:
                if fighter_name in self.object_df.loc[i, "red_fighter"]:
                    self.object_df.loc[i, "red_" + column] = fighter_stats_df.loc[
                        i, column
                    ]
                elif fighter_name in self.object_df.loc[i, "blue_fighter"]:
                    self.object_df.loc[i, "blue_" + column] = fighter_stats_df.loc[
                        i, column
                    ]

    def fill_missing_value(
        self, fighter_stats_df: pd.DataFrame, col_name: str, model: Any
    ) -> pd.DataFrame:
        """
        Generates a prediction for a missing value and adds it to the fighters dataframe.
        Uses the trained model for that stat.
        Args:
            fighter_stats_df (pd.DataFrame): The dataframe containing the average stats for a given fighter.
            col_name (str): Name of the column to fill in.
            model (Any): The trained model to use for the prediction.

        Returns:
            pd.DataFrame: The input df but with the missing value filled in.
        """
        # returns the predicted value.
        prediction = model.predict(
            fighter_stats_df.at[fighter_stats_df.index[1], col_name]
        )
        # Adds the predicted value to the dataframe.
        fighter_stats_df.at[fighter_stats_df.index[0], col_name] = prediction
        return fighter_stats_df

    def run_feature_engineering(self) -> None:
        """
        Method which executes the feature engineering.
        """
        # Contains all trained models for filling in missing values.
        models: Dict[str, RegressionModel] = self._fit_models()

        for fighter_name in self.fighters:
            # Gets each fighter and orders their fights, earliest to most recent.
            fighter = Fighter(self.object_df, fighter_name)

            # Fighter needs to have had at least 2 fights in order to fill in missing values.
            if len(fighter.fighter_df) > 1:
                # Gets the fighters stats in chronological order (as a fighter can be in both the red and blue corner)
                all_stats: DefaultDict[str, List[float]] = fighter.order_fighter_stats(
                    self.percent_stats
                )
                # Creates a dataframe containing the average stats for a given fighter.
                # but with the stats for their first fight in the UFC missing.
                fighter_stats_df: pd.DataFrame = fighter.setup_missing_val_df(all_stats)

                # ? There's probably a better way to do this
                # Using the trained model, predict what the stats for their first fight should be.
                fighter_stats_df = self.fill_missing_value(
                    fighter_stats_df, "sig_str_average", models["sig_strike"]
                )
                fighter_stats_df = self.fill_missing_value(
                    fighter_stats_df, "td_average", models["takedowns"]
                )
                fighter_stats_df = self.fill_missing_value(
                    fighter_stats_df,
                    "sig_strike_defence_average",
                    models["sig_strike_defence"],
                )
                fighter_stats_df = self.fill_missing_value(
                    fighter_stats_df, "td_defence_average", models["takedowns_defence"]
                )

                fighter_stats_df = fighter_stats_df.drop(
                    columns=self.percent_stats, axis=1
                )
                # Add these averages to the main dataframe iteratively by fighter.
                self._populate_averages_cols(fighter_stats_df, fighter_name)

        # Save the dataframe to a csv.
        self.object_df.to_csv(PathSettings.TRAINING_DATA_CSV, index=False)
