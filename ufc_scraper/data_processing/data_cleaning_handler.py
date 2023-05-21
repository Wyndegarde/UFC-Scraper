import re
from datetime import datetime
import numpy as np
import pandas as pd

from ufc_scraper.base_classes import DataFrameABC


class DataCleaningHandler(DataFrameABC):
    def __init__(self, csv_path: str, allow_creation: bool = False) -> None:
        super().__init__(csv_path, allow_creation)
        self.placeholder = "placeholder"

    def _clean_weight_class(self):
        pattern = re.compile(
            r"\d+|Tournament|Interim |UFC \
                |Australia |UK |vs. |Brazil |China \
                    |TUF Nations Canada |America |Latin \
                        |Ultimate Fighter  |Ultimate Fighter "
        )
        self.object_df["weight_class"] = self.object_df["weight_class"].apply(
            lambda x: pattern.sub("", x)
        )

    def get_height_reach_cols(self):
        return [
            column
            for column in self.object_df.columns
            if "Reach" in column or "Height" in column
        ]

    def get_drop_columns(self):
        drop_columns = []
        pattern = r"^---$"  # Pattern to match strings consisting of one or more dashes

        # Will drop the rows with missing days of birth for now. Return to this and investigate
        for column in self.object_df.columns:
            if any(re.match(pattern, str(value)) for value in self.object_df[column]):
                drop_columns.append(column)
                print(
                    column,
                    len(
                        self.object_df[column][
                            self.object_df[column].str.match(pattern)
                        ]
                    ),
                )

        return drop_columns

    def get_dob_cols(self):
        return [column for column in self.object_df.columns if "DOB" in column]

    def get_of_columns(self):
        of_columns = []
        for column in self.object_df.columns:
            type_condition = self.object_df[column].dtype == object
            of_condition = (
                sum(self.object_df[column].apply(lambda x: "of" in str(x))) > 0
            )
            name_condition = "fighter" not in column.lower()

            if type_condition and of_condition and name_condition:
                of_columns.append(column)

        return of_columns

    def handle_of_columns(self):
        of_columns = self.get_of_columns()
        for (
            column
        ) in (
            of_columns
        ):  # This block converts all the columns from strings containing "x of y" to two columns corresponding to attempted and landed.
            column_as_list = self.object_df[column].tolist()
            splitting_column = [each.split(" of ") for each in column_as_list]
            attempted = [float(i[1]) for i in splitting_column]
            landed = [float(i[0]) for i in splitting_column]

            attempted_suffix = column + "_attempted"
            landed_suffix = column + "_landed"
            percent_suffix = column + "_percent"

            self.object_df[attempted_suffix] = attempted
            self.object_df[landed_suffix] = landed
            self.object_df[percent_suffix] = (
                self.object_df[landed_suffix] / self.object_df[attempted_suffix]
            )
            self.object_df[percent_suffix] = self.object_df[percent_suffix].fillna(0)

            self.object_df.drop(columns=column, inplace=True)

    # Convert both reach columns into cm
    def _convert_reach(self, reach):
        if reach == "--":
            return np.nan
        clean_reach = float(reach.replace('"', ""))
        return clean_reach * 2.54

    def _convert_height(self, height: str) -> float:
        """
        Converts a height in feet'inches to centimeters.
        """
        if height == "--":
            return 0
        feet_str, inches_str = height.split("'")
        feet = int(feet_str)
        inches = int(inches_str.replace('"', ""))
        return round((feet * 12 + inches) * 2.54, 0)

    def drop_unwanted_data(self, drop_columns):
        """
        Drops columns that are not needed for the model.
        """
        self.object_df = self.object_df[self.object_df["blue_DOB"] != "--"]
        self.object_df = self.object_df[self.object_df["red_DOB"] != "--"]
        self.object_df.drop(drop_columns, axis=1, inplace=True)

    def format_date_columns(self):
        """
        Formats the date columns to datetime objects.
        """
        self.object_df["date"] = self.object_df["date"].apply(
            lambda x: datetime.strptime(x, "%B %d, %Y")
        )
        for column in self.object_df.columns:
            if "DOB" in column:
                self.object_df[column] = self.object_df[column].apply(
                    lambda x: datetime.strptime(x, "%b %d, %Y")
                )

    def run_pipeline(self):
        self.object_df.replace("---", "0", inplace=True)
        self.handle_of_columns()
        self._clean_weight_class()
        height_reach_cols = [
            column
            for column in self.object_df.columns
            if "Reach" in column or "Height" in column
        ]
        self.object_df.dropna(subset=height_reach_cols, inplace=True)
        for column in height_reach_cols:
            if "Height" in column:
                self.object_df[column] = self.object_df[column].apply(
                    self._convert_height
                )
            else:
                self.object_df[column] = self.object_df[column].apply(
                    self._convert_reach
                )

        percent_cols = [col for col in self.object_df.columns if "%" in col]
        print(percent_cols)
        for column in percent_cols:
            self.object_df[column] = (
                self.object_df[column].str.strip("%").astype("int") / 100
            )

        self.object_df["blue_STANCE"].replace(np.nan, "Orthodox", inplace=True)
        self.object_df["red_STANCE"].replace(np.nan, "Orthodox", inplace=True)
        self.object_df.drop(
            self.object_df[self.object_df["blue_DOB"] == "--"].index[0], inplace=True
        )
        self.object_df.drop(
            self.object_df[self.object_df["red_DOB"] == "--"].index[0], inplace=True
        )
        # self.object_df.replace("---", "0", inplace=True)

        height_columns = [
            column for column in self.object_df.columns if "Height" in column
        ]
        reach_columns = [
            column for column in self.object_df.columns if "Reach" in column
        ]

        self.object_df["Height_diff"] = (
            self.object_df[height_columns[0]] - self.object_df[height_columns[1]]
        )  # Red height minus Blue height. So positve value suggests red taller, negative implies red shorter.
        self.object_df["Reach_diff"] = (
            self.object_df[reach_columns[0]] - self.object_df[reach_columns[1]]
        )  # Same as for height.

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

        # I need: strike defence and takedown defence for red and blue fighters

        self.object_df["red_sig_strike_defence_percent"] = (
            1 - self.object_df["blue_sig_strike_percent"]
        )
        self.object_df["blue_sig_strike_defence_percent"] = (
            1 - self.object_df["red_sig_strike_percent"]
        )

        self.object_df["red_takedowns_defence_percent"] = (
            1 - self.object_df["blue_takedowns_percent"]
        )
        self.object_df["blue_takedowns_defence_percent"] = (
            1 - self.object_df["red_takedowns_percent"]
        )

        # number_of_fights_per_fighter = (
        #     self.object_df["red_fighter"]
        #     .append(self.object_df["blue_fighter"])
        #     .value_counts()
        # )

        pd.write_csv(self.object_df, "cleaned_data.csv")
