import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from ufc_scraper.base_classes import DataFrameABC

"""
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
            column.replace("red_", "").replace("_blue", "")
            for column in self.object_df.columns
            if "%" in column
        ]

    def _get_fighter(self, fighter_name: str) -> pd.DataFrame:
        return self.object_df[
            (self.object_df["red_fighter"] == fighter_name)
            | (self.object_df["blue_fighter"] == fighter_name)
        ].sort_values(by="date", ascending=True)

    def _build_regression_df(self) -> pd.DataFrame:
        regression_df = pd.DataFrame()
        for column in self.percent_stats:
            each_stat_df = pd.DataFrame(
                columns=[column, "Y_" + column, "X_" + column]
            )  # Builds a dataframe for each stat.
            for fighter in self.fighters:
                fighter_df = self._get_fighter(fighter)

                if len(fighter_df) >= 3:
                    ordered_stats = []

                    for i in fighter_df.index:
                        if fighter in fighter_df.loc[i, "red_fighter"]:
                            ordered_stats.append(fighter_df.loc[i, "red_" + column])
                        if fighter in fighter_df.loc[i, "blue_fighter"]:
                            ordered_stats.append(fighter_df.loc[i, "blue_" + column])

                    lin_reg_df = pd.DataFrame(
                        ordered_stats, columns=[column]
                    )  # Goes through and builds the X and Y data for the linear regression model.
                    lin_reg_df["X_" + column] = (
                        lin_reg_df[column].expanding(2).mean().shift(1)
                    )
                    lin_reg_df.loc[1, "X_" + column] = lin_reg_df.loc[0, column]
                    lin_reg_df["Y_" + column] = lin_reg_df["X_" + column].shift(1)
                    lin_reg_df = lin_reg_df.dropna()

                    each_stat_df = pd.concat(
                        [each_stat_df, lin_reg_df], axis=0
                    )  # Adds the rows of each fighter to the dataframe for that stat.

                regression_df = pd.concat(
                    [regression_df, each_stat_df], axis=1
                )  # Adds the columns for each stat to the master DF.

                regression_df = regression_df.reset_index(
                    drop=True
                )  # Just resets the index.

                XYs_only = regression_df.drop(self.percent_stats, axis=1)

        return XYs_only

    def migration_placeholder(self):
        XYs_only = self._build_regression_df()
        sig_strike_model = smf.ols(
            "Y_sig_strike_percent	~ X_sig_strike_percent", data=XYs_only
        ).fit()
        takedowns_model = smf.ols(
            "Y_takedowns_percent	~ X_takedowns_percent", data=XYs_only
        ).fit()
        sig_strike_defence_model = smf.ols(
            "Y_sig_strike_defence_percent	~ X_sig_strike_defence_percent", data=XYs_only
        ).fit()
        takedowns_defence_model = smf.ols(
            "Y_takedowns_defence_percent	~ X_takedowns_defence_percent", data=XYs_only
        ).fit()

        red_blue_percent_stats = []
        for column in self.object_df.columns:
            if "percent" in column and "total" not in column:
                red_blue_percent_stats.append(column)
        new_columns = []
        for name in red_blue_percent_stats:
            string = name.replace("percent", "average")
            new_columns.append(string)
            self.object_df[string] = np.nan

        for fighter in self.fighters:
            fighter_df = self._get_fighter(
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
                exog=dict(X_takedowns_percent=df.loc[df.index[1], "takedowns_average"])
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
            df.loc[df.index[0], "takedowns_defence_average"] = predict_takedown_defence[
                0
            ]

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


class FeatureEngineering(DataFrameABC):
    def get_unique_fighters(self):
        """
        Responsible for holding the unique fighter names.
        """
        return np.unique(
            np.concatenate(
                [self.object_df["red_fighter"], self.object_df["blue_fighter"]],
                axis=None,
            )
        )

    def get_percent_cols(self):
        """
        Responsible for holding the column names of the percent stats.
        """
        percent_columsn = list(
            set(
                [
                    column.replace("red_", "").replace("_blue", "")
                    for column in self.object_df.columns
                    if "%" in column
                ]
            )
        )
        return percent_columsn

def populate_regression_df(x):
    """
    1. Instantiate new dataframe.
    2. iterate through the percent stats columns
    3. iterate through each fighter.
    4. check if the fighter has more than 3 fights.
    5. if so, build a dataframe for that fighter.
    """

    def create_fighter_df():
        """
        Responsible for creating a dataframe for each fighter.
        end result is a df containing the stats for a fighter with more than three fights.
        """
        ...

    main_df = pd.DataFrame()
    if x >= 3:
        new_df = create_fighter_df()

    main_df = pd.concat([main_df, new_df], axis=1)

    return main_df


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
