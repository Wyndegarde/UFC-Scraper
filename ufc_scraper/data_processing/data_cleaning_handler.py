import re
from datetime import datetime
import numpy as np

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

    def _display_total_placeholder_values(self):
        drop_columns = []
        # Will drop the rows with missing days of birth for now. Return to this and investigate
        for column in self.object_df.columns:
            if len(self.object_df[column][self.object_df[column] == "--"]) > 0:
                print(
                    column, len(self.object_df[column][self.object_df[column] == "--"])
                )
            if len(self.object_df[column][self.object_df[column] == "---"]) > 0:
                drop_columns.append(column)
                print(
                    column, len(self.object_df[column][self.object_df[column] == "---"])
                )

        return drop_columns

    def get_height_reach_cols(self):
        height_reach = []
        for column in self.object_df.columns:
            if "Reach" in column or "Height" in column:
                height_reach.append(column)
        return height_reach

    # Convert both reach columns into cm
    def _convert_reach(self, reach):
        # bit of a messy change, but currently I replace all of these strings with NaN, then work out the newly mean of the column excluding these values and finally replace the NaN with the mean.
        if reach == "--":
            return np.nan
        else:
            clean_reach = float(reach.replace('"', ""))
            return clean_reach * 2.54

    def _convert_height_to_cm(self, height: str) -> float:
        """
        Converts a height in feet'inches to centimeters.
        """
        if height == "--":
            return 0
        else:
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

    def replace_nan_values(self):
        """
        Replaces all NaN values with 0.
        """
        self.object_df = self.object_df.replace("---", "0")
        self.object_df["blue_STANCE"] = self.object_df["blue_STANCE"].replace(
            np.nan, "Orthodox"
        )  # Choosing the replace with Orthodox because it is the most common stance.
        self.object_df["red_STANCE"] = self.object_df["blue_STANCE"].replace(
            np.nan, "Orthodox"
        )  # see above

    def clean_columns(self):
        # This block here pulls all the percentage columns, then removes the % from each and converts them to decimal.
        percent_names = []
        of_columns = []
        height_columns = []
        reach_columns = []

        for name in self.object_df.columns:
            if "percent" in name:
                percent_names.append(name)
            # This is definitely not the best way to do this, find better way.
            elif (
                self.object_df[name].dtype == object
                and sum(self.object_df[name].apply(lambda x: "of" in str(x))) > 0
                and name != "red_fighter"
                and name != "blue_fighter"
            ):
                # This block gets all the columns with ' x of y' in them and stores them in a list for processing.
                of_columns.append(name)

            elif (
                "Height" in name
            ):  # This block converts the height and reach columns from inches to cm.
                height_columns.append(name)
                self.object_df[name] = self.object_df[name].apply(
                    lambda x: self._convert_height_to_cm(x)
                )

            elif "Reach" in name:
                reach_columns.append(name)
                self.object_df[name] = self.object_df[name].apply(
                    lambda x: self._convert_reach(x)
                )

            for column in percent_names:
                self.object_df[column] = (
                    self.object_df[column].str.strip("%").astype("int") / 100
                )
