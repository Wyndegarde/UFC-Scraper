import re
from datetime import datetime

import numpy as np

from pathlib import Path


from ufc_scraper.base_classes import DataFrameABC
from ufc_scraper.config import PathSettings


class DataProcessor(DataFrameABC):
    def __init__(self, csv_path: Path, allow_creation: bool = False) -> None:
        super().__init__(csv_path, allow_creation)

        if (not allow_creation) and (self.object_df.empty):
            raise ValueError("DataFrame must not be empty")

        self.height_reach_cols = [
            column
            for column in self.object_df.columns
            if "reach" in column.lower() or "height" in column.lower()
        ]

    def _create_height_reach_na_filler_df(self):
        reach_height_df = self.object_df.copy()
        reach_height_df.dropna(subset=self.height_reach_cols, inplace=True)
        self._apply_hr_conversions(reach_height_df)
        grouping_by_weight_classes = reach_height_df.groupby("weight_class")[
            self.height_reach_cols
        ].mean()

        return grouping_by_weight_classes[self.height_reach_cols]

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

    def _get_dob_cols(self):
        return [column for column in self.object_df.columns if "DOB" in column]

    def _get_attempt_landed_columns(self):
        attempt_landed_columns = []
        for column in self.object_df.columns:
            type_condition = self.object_df[column].dtype == object
            of_condition = (
                sum(self.object_df[column].apply(lambda x: "of" in str(x))) > 0
            )
            name_condition = "fighter" not in column.lower()

            if type_condition and of_condition and name_condition:
                attempt_landed_columns.append(column)

        return attempt_landed_columns

    def _handle_attempt_landed_columns(self):
        attempt_landed_columns = self._get_attempt_landed_columns()
        # This block converts all the columns from strings containing "x of y" to two columns corresponding to attempted and landed.
        for column in attempt_landed_columns:
            splitting_column = self.object_df[column].apply(lambda x: x.split(" of "))
            attempted = splitting_column.apply(lambda x: float(x[1]))
            landed = splitting_column.apply(lambda x: float(x[0]))

            attempted_suffix = f"{column}_attempted"
            landed_suffix = f"{column}_landed"
            percent_suffix = f"{column}_percent"

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

    def _apply_hr_conversions(self, dataframe):
        for column in self.height_reach_cols:
            if "Height" in column:
                dataframe[column] = dataframe[column].apply(self._convert_height)
            else:
                dataframe[column] = dataframe[column].apply(self._convert_reach)

    def _handle_height_reach(self, height_reach_no_na_df):
        self._apply_hr_conversions(self.object_df)

        missing_indices = self.object_df.index[
            self.object_df[self.height_reach_cols].isna().any(axis=1)
        ]

        for column in self.height_reach_cols:
            for i in missing_indices:
                if np.isnan(self.object_df.loc[i, column]):
                    self.object_df.loc[i, column] = height_reach_no_na_df.loc[
                        self.object_df.loc[i, "weight_class"], column
                    ]

        height_columns = [self.height_reach_cols[0], self.height_reach_cols[2]]
        reach_columns = [self.height_reach_cols[1], self.height_reach_cols[3]]

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
