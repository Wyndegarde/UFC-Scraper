"""
Module responsible for cleaning the raw data scraped from the web.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import numpy as np

from src.lib.processing import CSVProcessingHandler
from src.config import PathSettings
from src.lib.engines.constants import UFC_KEY_COLUMNS, NEXT_EVENT_KEY_COLUMNS


class DataCleaningEngine(CSVProcessingHandler):
    """
    Reads in the raw data scraped from the web and cleans it.

    Args:
        CSVProcessingHandler: Class containing functionality for all csv data.
    """

    def __init__(self, csv_path: Path, allow_creation: bool = False) -> None:
        super().__init__(csv_path, allow_creation)

        # Additional flag for where an error occurs during scraping and data isn't saved
        if (not allow_creation) and (self.df.empty):
            raise ValueError("DataFrame must not be empty")

    def clean_raw_data(self):
        # Data source represent no attempts as "---".
        self.df.replace("---", "0", inplace=True)

        # Special bouts have things like TUF in the weight class. This removes that.
        # self._clean_weight_class()

        # Simply converts the date columns to datetime objects.
        # self._format_date_columns()

        # Data source has stats as "x of y". Split these into two cols.
        self._handle_attempt_landed_columns()

        # small subset of rows have missing values for height and reach.
        # Drops these for accuracy.
        # height_reach_no_na_df = self._create_height_reach_na_filler_df()
        # self._handle_height_reach(height_reach_no_na_df)

        # Creates columns for the age of each fighter.
        # self._create_age_columns()

        # Converts cols with % in them to floats.
        self._handle_percent_columns()

        # Where missing, the stance is changed to the most common stance.
        # self.df["blue_STANCE"].replace(np.nan, "Orthodox", inplace=True)
        # self.df["red_STANCE"].replace(np.nan, "Orthodox", inplace=True)

        # number_of_fights_per_fighter = (
        #     self.df["red_fighter"]
        #     .append(self.df["blue_fighter"])
        #     .value_counts()
        # )

        # Clean the column names
        # self.df.columns = (
        #     self.df.columns.str.replace(".", "").str.replace(" ", "_").str.lower()
        # )
        # Using only the columns necessary for the model.
        self.df = self.df[UFC_KEY_COLUMNS]
        self.df.to_csv(PathSettings.CLEAN_DATA_CSV, index=False)
        # return self.df

    def clean_next_event(self):

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

        self.df = self.df[NEXT_EVENT_KEY_COLUMNS]
        self.df.rename(columns=column_mapper, inplace=True)
        percent_cols = [col for col in self.df.columns if "average" in col]
        for column in percent_cols:
            self.df[column] = self.df[column].str.strip("%").astype("int") / 100
        # Where missing, the stance is changed to the most common stance.
        self.df["blue_stance"].replace(np.nan, "Orthodox", inplace=True)
        self.df["red_stance"].replace(np.nan, "Orthodox", inplace=True)
        self._clean_weight_class()
        self._format_date_columns()
        # self._apply_hr_conversions(self.df, height_reach_cols=height_reach_cols)
        # self._create_height_reach_diff_columns(height_reach_cols=height_reach_cols)

    def _get_attempt_landed_columns(self) -> List[str]:
        """
        Finds all columns where the values look like "x of y"
        """
        attempt_landed_columns: List[str] = []

        # Separated out conditions for clarity.
        for column in self.df.columns:
            # Ensure the column is a string column.
            type_condition: bool = self.df[column].dtype == object

            # Ensure at least one of the values contains "of".
            of_condition: bool = (
                sum(self.df[column].apply(lambda x: "of" in str(x))) > 0
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
            splitting_column = self.df[column].apply(lambda x: x.split(" of "))
            attempted = splitting_column.apply(lambda x: float(x[1]))
            landed = splitting_column.apply(lambda x: float(x[0]))

            attempted_suffix: str = f"{column}_attempted"
            landed_suffix: str = f"{column}_landed"
            percent_suffix: str = f"{column}_percent"

            self.df[attempted_suffix] = attempted
            self.df[landed_suffix] = landed
            self.df[percent_suffix] = self.df[landed_suffix] / self.df[attempted_suffix]
            self.df[percent_suffix] = self.df[percent_suffix].fillna(0)

            self.df.drop(columns=column, inplace=True)

    def _handle_percent_columns(self):
        percent_cols = [col for col in self.df.columns if "%" in col]
        for column in percent_cols:
            self.df[column] = self.df[column].str.strip("%").astype("int") / 100
        # I need: strike defence and takedown defence for red and blue fighters
        self.df["red_sig_strike_defence_percent"] = 1 - self.df["blue_Sig. str. %"]
        self.df["blue_sig_strike_defence_percent"] = 1 - self.df["red_Sig. str. %"]

        self.df["red_td_defence_percent"] = 1 - self.df["blue_Td %"]
        self.df["blue_td_defence_percent"] = 1 - self.df["red_Td %"]
