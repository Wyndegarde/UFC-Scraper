"""
Module responsible for cleaning the raw data scraped from the web.
"""
from datetime import datetime
import re
from typing import List

import pandas as pd
import numpy as np

from pathlib import Path

from src.lib.abstract import DataFrameABC
from src.config import PathSettings


class DataCleaner(DataFrameABC):
    """
    Reads in the raw data scraped from the web and cleans it.

    Args:
        DataFrameABC: Base class containing shared functionality for all dataframes.
    """

    def __init__(self, csv_path: Path, allow_creation: bool = False) -> None:
        super().__init__(csv_path, allow_creation)

        # Additional flag for where an error occurs during scraping and data isn't saved
        if (not allow_creation) and (self.object_df.empty):
            raise ValueError("DataFrame must not be empty")

    def _get_height_reach_cols(self) -> List[str]:
        """
        Extracts the height and reach columns from the dataframe.
        Makes it easier to work with due to red/blue prefixes.
        """
        return [
            column
            for column in self.object_df.columns
            if "reach" in column.lower() or "height" in column.lower()
        ]

    def _create_height_reach_na_filler_df(self) -> pd.DataFrame:
        """
        Creates a new dataframe for filling in missing values for height and reach cols.
        Uses the overall means, separated out by weight class.

        Returns:
            pd.DataFrame: A dataframe with the mean height and reach for each weight class.
        """
        height_reach_cols: List[str] = self._get_height_reach_cols()

        # Take a copy of the original df and drop all rows with missing values for height and reach.
        reach_height_df: pd.DataFrame = self.object_df.copy()
        reach_height_df.dropna(subset=height_reach_cols, inplace=True)
        self._apply_hr_conversions(reach_height_df, height_reach_cols)

        # group by weight class and take the mean of the height and reach columns.
        grouping_by_weight_classes: pd.DataFrame = reach_height_df.groupby(
            "weight_class"
        )[height_reach_cols].mean()

        return grouping_by_weight_classes[height_reach_cols]

    def _clean_weight_class(self) -> None:
        """
        Some events have stray words in the weight class column.
        This removes them.
        """
        pattern: re.Pattern = re.compile(
            r"\d+|Tournament|Interim |UFC \
                |Australia |UK |vs. |Brazil |China \
                    |TUF Nations Canada |America |Latin \
                        |Ultimate Fighter  |Ultimate Fighter "
        )
        self.object_df["weight_class"] = self.object_df["weight_class"].apply(
            lambda x: pattern.sub("", x)
        )

    def _get_dob_cols(self) -> List[str]:
        """
        Overkill but gets the red/blue DOB columns.
        """
        return [column for column in self.object_df.columns if "DOB" in column]

    def _get_attempt_landed_columns(self) -> List[str]:
        """
        Finds all columns where the values look like "x of y"
        """
        attempt_landed_columns: List[str] = []

        # Separated out conditions for clarity.
        for column in self.object_df.columns:
            # Ensure the column is a string column.
            type_condition: bool = self.object_df[column].dtype == object

            # Ensure at least one of the values contains "of".
            of_condition: bool = (
                sum(self.object_df[column].apply(lambda x: "of" in str(x))) > 0
            )

            # Some fighters can have "of" in their name. Don't want that
            name_condition: bool = "fighter" not in column.lower()

            if type_condition and of_condition and name_condition:
                attempt_landed_columns.append(column)

        return attempt_landed_columns

    def _handle_attempt_landed_columns(self) -> None:
        """
        Breaks up the columns where the values are strings like "x of y".
        """
        attempt_landed_columns: List[str] = self._get_attempt_landed_columns()
        # This block converts all the columns from strings containing "x of y" to two columns corresponding to attempted and landed.
        for column in attempt_landed_columns:
            splitting_column = self.object_df[column].apply(lambda x: x.split(" of "))
            attempted = splitting_column.apply(lambda x: float(x[1]))
            landed = splitting_column.apply(lambda x: float(x[0]))

            attempted_suffix: str = f"{column}_attempted"
            landed_suffix: str = f"{column}_landed"
            percent_suffix: str = f"{column}_percent"

            self.object_df[attempted_suffix] = attempted
            self.object_df[landed_suffix] = landed
            self.object_df[percent_suffix] = (
                self.object_df[landed_suffix] / self.object_df[attempted_suffix]
            )
            self.object_df[percent_suffix] = self.object_df[percent_suffix].fillna(0)

            self.object_df.drop(columns=column, inplace=True)

    def _convert_reach(self, reach):
        # Convert both reach columns into cm
        if reach == "--":
            return np.nan
        clean_reach = float(reach.replace('"', ""))
        return clean_reach * 2.54

    def _convert_height(self, height: str) -> float:
        """
        Converts a height in feet'inches to centimeters.
        """
        if height == "--":
            return np.nan
        feet_str, inches_str = height.split("'")
        feet = int(feet_str)
        inches = int(inches_str.replace('"', ""))
        return round((feet * 12 + inches) * 2.54, 0)

    def _apply_hr_conversions(
        self, dataframe: pd.DataFrame, height_reach_cols: List[str]
    ):
        for column in height_reach_cols:
            if "height" in column.lower():
                dataframe[column] = dataframe[column].apply(self._convert_height)
            else:
                dataframe[column] = dataframe[column].apply(self._convert_reach)

    def _create_height_reach_diff_columns(self, height_reach_cols):
        height_columns = [height_reach_cols[0], height_reach_cols[2]]
        reach_columns = [height_reach_cols[1], height_reach_cols[3]]

        self.object_df["height_diff"] = (
            self.object_df[height_columns[0]] - self.object_df[height_columns[1]]
        )  # Red height minus Blue height. So positve value suggests red taller, negative implies red shorter.
        self.object_df["reach_diff"] = (
            self.object_df[reach_columns[0]] - self.object_df[reach_columns[1]]
        )  # Same as for height.

    def _handle_height_reach(self, height_reach_no_na_df: pd.DataFrame) -> None:
        height_reach_cols: List[str] = self._get_height_reach_cols()
        self._apply_hr_conversions(self.object_df, height_reach_cols)

        missing_indices = self.object_df.index[
            self.object_df[height_reach_cols].isna().any(axis=1)
        ]

        for column in height_reach_cols:
            for i in missing_indices:
                if np.isnan(self.object_df.loc[i, column]):
                    self.object_df.loc[i, column] = height_reach_no_na_df.loc[
                        self.object_df.loc[i, "weight_class"], column
                    ]

        self._create_height_reach_diff_columns(height_reach_cols)

    def _create_age_columns(self):
        self.object_df["red_age"] = (
            self.object_df["date"]
            .sub(self.object_df["red_DOB"])
            .dt.days.div(365.25)
            .round(0)
            .astype(int)
        )
        self.object_df["blue_age"] = (
            self.object_df["date"]
            .sub(self.object_df["blue_DOB"])
            .dt.days.div(365.25)
            .round(0)
            .astype(int)
        )

    def _format_date_columns(self):
        """
        Formats the date columns to datetime objects.
        """
        self.object_df["date"] = self.object_df["date"].apply(
            lambda x: datetime.strptime(x, "%B %d, %Y")
        )
        self.object_df.drop(
            self.object_df[self.object_df["blue_DOB"] == "--"].index, inplace=True
        )
        self.object_df.drop(
            self.object_df[self.object_df["red_DOB"] == "--"].index, inplace=True
        )
        for column in self.object_df.columns:
            if "DOB" in column:
                self.object_df[column] = self.object_df[column].apply(
                    lambda x: datetime.strptime(x, "%b %d, %Y")
                )

    def _handle_percent_columns(self):
        percent_cols = [col for col in self.object_df.columns if "%" in col]
        for column in percent_cols:
            self.object_df[column] = (
                self.object_df[column].str.strip("%").astype("int") / 100
            )
        # I need: strike defence and takedown defence for red and blue fighters
        self.object_df["red_sig_strike_defence_percent"] = (
            1 - self.object_df["blue_Sig. str. %"]
        )
        self.object_df["blue_sig_strike_defence_percent"] = (
            1 - self.object_df["red_Sig. str. %"]
        )

        self.object_df["red_td_defence_percent"] = 1 - self.object_df["blue_Td %"]
        self.object_df["blue_td_defence_percent"] = 1 - self.object_df["red_Td %"]

    def _fill_na_values(self, height_reach):
        grouped_df = self.object_df.copy()
        grouped_df = grouped_df.dropna(subset=height_reach)

        grouping_by_weight_classes = grouped_df.groupby("weight_class").mean()
        reach_height_df = grouping_by_weight_classes[height_reach]
        missing_value_df = self.object_df.copy()
        missing_value_df = missing_value_df[missing_value_df.isna().any(axis=1)]
        missing_value_df = missing_value_df[height_reach]

        for column in height_reach:
            for i in missing_value_df.index:
                if np.isnan(missing_value_df.loc[i, column]):
                    self.object_df.loc[i, column] = reach_height_df.loc[
                        self.object_df.loc[i, "weight_class"], column
                    ]

    def clean_raw_data(self):
        # Data source represent no attempts as "---".
        self.object_df.replace("---", "0", inplace=True)

        # Special bouts have things like TUF in the weight class. This removes that.
        self._clean_weight_class()

        # Simply converts the date columns to datetime objects.
        self._format_date_columns()

        # Data source has stats as "x of y". Split these into two cols.
        self._handle_attempt_landed_columns()

        # small subset of rows have missing values for height and reach.
        # Drops these for accuracy.
        height_reach_no_na_df = self._create_height_reach_na_filler_df()
        self._handle_height_reach(height_reach_no_na_df)

        # Creates columns for the age of each fighter.
        self._create_age_columns()

        # Converts cols with % in them to floats.
        self._handle_percent_columns()

        # Where missing, the stance is changed to the most common stance.
        self.object_df["blue_STANCE"].replace(np.nan, "Orthodox", inplace=True)
        self.object_df["red_STANCE"].replace(np.nan, "Orthodox", inplace=True)

        # number_of_fights_per_fighter = (
        #     self.object_df["red_fighter"]
        #     .append(self.object_df["blue_fighter"])
        #     .value_counts()
        # )

        # Clean the column names
        self.object_df.columns = (
            self.object_df.columns.str.replace(".", "")
            .str.replace(" ", "_")
            .str.lower()
        )
        # Using only the columns necessary for the model.
        UFC_key_columns = [
            "date",
            "red_fighter",
            "blue_fighter",
            "winner",
            "red_sig_str_percent",
            "blue_sig_str_percent",
            "red_sub_att",
            "blue_sub_att",
            "red_stance",
            "blue_stance",
            "red_total_str_percent",
            "blue_total_str_percent",
            "red_td_percent",
            "blue_td_percent",
            "height_diff",
            "reach_diff",
            "red_age",
            "blue_age",
            "red_sig_strike_defence_percent",
            "blue_sig_strike_defence_percent",
            "red_td_defence_percent",
            "blue_td_defence_percent",
        ]
        self.object_df = self.object_df[UFC_key_columns]
        self.object_df.to_csv(PathSettings.CLEAN_DATA_CSV, index=False)
        # return self.object_df

    def clean_next_event(self):
        # Lazy way of doing this rn. cba finding more elegant solution.
        next_event_key_columns = [
            "date",
            "location",
            "red_fighter",
            "blue_fighter",
            "weight_class",
            "title_bout",
            "red_Striking Accuracy",
            "blue_Striking Accuracy",
            "red_Defense",
            "blue_Defense",
            "red_Takedown Accuracy",
            "blue_Takedown Accuracy",
            "red_Takedown Defense",
            "blue_Takedown Defense",
            "red_Stance",
            "blue_Stance",
            "red_DOB",
            "blue_DOB",
            "red_Height",
            "blue_Height",
            "red_Reach",
            "blue_Reach",
            "red_record",
            "blue_record",
        ]

        column_mapper = {
            "red_Striking Accuracy": "red_sig_str_average",
            "blue_Striking Accuracy": "blue_sig_str_average",
            "red_Defense": "red_sig_strike_defence_average",
            "blue_Defense": "blue_sig_strike_defence_average",
            "red_Takedown Accuracy": "red_td_average",
            "blue_Takedown Accuracy": "blue_td_average",
            "red_Takedown Defense": "red_td_defence_average",
            "blue_Takedown Defense": "blue_td_defence_average",
            "red_Stance": "red_stance",
            "blue_Stance": "blue_stance",
        }
        height_reach_cols = self._get_height_reach_cols()

        self.object_df = self.object_df[next_event_key_columns]
        self.object_df.rename(columns=column_mapper, inplace=True)
        percent_cols = [col for col in self.object_df.columns if "average" in col]
        for column in percent_cols:
            self.object_df[column] = (
                self.object_df[column].str.strip("%").astype("int") / 100
            )
        # Where missing, the stance is changed to the most common stance.
        self.object_df["blue_stance"].replace(np.nan, "Orthodox", inplace=True)
        self.object_df["red_stance"].replace(np.nan, "Orthodox", inplace=True)
        self._clean_weight_class()
        self._format_date_columns()
        self._apply_hr_conversions(self.object_df, height_reach_cols=height_reach_cols)
        self._create_height_reach_diff_columns(height_reach_cols=height_reach_cols)
