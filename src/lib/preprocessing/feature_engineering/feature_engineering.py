from typing import List, DefaultDict, Dict
import numpy as np
import pandas as pd

from src.lib.data_managers import CSVProcessingHandler
from src.config import PathSettings
from .regression import RegressionModel
from .fighter import Fighter


class FeatureEngineering(CSVProcessingHandler):
    def __init__(self, csv_path, allow_creation) -> None:
        super().__init__(csv_path, allow_creation)
        # Returns a list of all unique fighters in the dataframe
        self.fighters = np.unique(
            np.concatenate(
                [self.df["red_fighter"], self.df["blue_fighter"]],
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
            for column in self.df.columns
            if "percent" in column
        ]
        # Quick way to drop the duplicates - changes the order tho but not important here
        return list(set(percent_stats))

    def run(self) -> None:
        """
        Executes the feature engineering process by filling missing values and updating the main DataFrame.
        """
        models: Dict[str, RegressionModel] = self._fit_models()

        # Define stat columns and their corresponding models
        stat_model_mapping = {
            "sig_str_average": "sig_strike",
            "td_average": "takedowns",
            "sig_strike_defence_average": "sig_strike_defence",
            "td_defence_average": "takedowns_defence",
        }

        for fighter_name in self.fighters:
            fighter = Fighter(self.df, fighter_name)

            if len(fighter.fighter_df) <= 1:
                continue

            all_stats = fighter.order_fighter_stats(self.percent_stats)
            fighter_stats_df = fighter.setup_missing_val_df(all_stats)

            # Fill missing values for each stat using corresponding model
            for stat_col, model_name in stat_model_mapping.items():
                fighter_stats_df = self.fill_missing_value(
                    fighter_stats_df, stat_col, models[model_name]
                )

            fighter_stats_df = fighter_stats_df.drop(columns=self.percent_stats, axis=1)
            self._populate_averages_cols(fighter_stats_df, fighter_name)

        self.df.to_csv(PathSettings.TRAINING_DATA_CSV, index=False)

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
            fighter: Fighter = Fighter(self.df, fighter_name)

            # Can only create a fighters regression df if they have had at least 3 fights.
            if len(fighter.fighter_df) >= 3:
                # Gets the fighters stats in chronological order (as a fighter can be in both the red and blue corner)
                ordered_stats: DefaultDict[str, List[float]] = (
                    fighter.order_fighter_stats(self.percent_stats)
                )

                # Manipulate the ordered stats to create the X and Y columns for each stat.
                fighter_lin_reg_df = fighter.create_fighter_reg_df(ordered_stats)

                # Add the fighters X and Y columns to the overall regression df.
                regression_df = pd.concat([regression_df, fighter_lin_reg_df], axis=0)

        # return the final dataframe with reset index (so index 1 corresponds to row 1, not the row index of input df)
        return regression_df.reset_index(drop=True)

    def _fit_models(self) -> Dict[str, RegressionModel]:
        """
        Method to create the linear regression models that will predict missing values.
        Returns:
            Dict[str, RegressionModel]: Dictionary of trained regression models for each stat type.
        """
        XYs_only = self._build_regression_df()

        # Define model configurations
        model_configs = {
            "sig_strike": ("X_sig_str_percent", "Y_sig_str_percent"),
            "takedowns": ("X_td_percent", "Y_td_percent"),
            "sig_strike_defence": (
                "X_sig_strike_defence_percent",
                "Y_sig_strike_defence_percent",
            ),
            "takedowns_defence": ("X_td_defence_percent", "Y_td_defence_percent"),
        }

        # Create models using configuration
        return {
            name: RegressionModel(XYs_only, x_col, y_col)
            for name, (x_col, y_col) in model_configs.items()
        }

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
                if fighter_name in self.df.loc[i, "red_fighter"]:
                    self.df.loc[i, "red_" + column] = fighter_stats_df.loc[i, column]
                elif fighter_name in self.df.loc[i, "blue_fighter"]:
                    self.df.loc[i, "blue_" + column] = fighter_stats_df.loc[i, column]

    def fill_missing_value(
        self, fighter_stats_df: pd.DataFrame, col_name: str, model: RegressionModel
    ) -> pd.DataFrame:
        """
        Generates and adds a prediction for a missing value using the trained model.

        Args:
            fighter_stats_df: DataFrame containing fighter's average stats
            col_name: Name of the column to fill
            model: Trained regression model for prediction

        Returns:
            DataFrame with the missing value filled
        """
        first_valid_stat = fighter_stats_df.at[fighter_stats_df.index[1], col_name]
        prediction = model.predict(first_valid_stat)
        fighter_stats_df.at[fighter_stats_df.index[0], col_name] = prediction
        return fighter_stats_df
