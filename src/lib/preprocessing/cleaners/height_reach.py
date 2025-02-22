from typing import List
import pandas as pd
import numpy as np
from .abstract import CleanerABC


class HeightReachCleaner(CleanerABC):
    def clean(self): ...

    def get_height_reach_avgs(self) -> pd.DataFrame:
        """
        Creates a new dataframe for filling in missing values for height and reach cols.
        Uses the overall means, separated out by weight class.

        Returns:
            pd.DataFrame: A dataframe with the mean height and reach for each weight class.
        """
        height_reach_cols: List[str] = self._get_height_reach_cols()

        # Take a copy of the original df and drop all rows with missing values for height and reach.
        reach_height_df: pd.DataFrame = self.df.copy()
        reach_height_df.dropna(subset=height_reach_cols, inplace=True)
        self._convert_to_cm(reach_height_df, height_reach_cols)

        # group by weight class and take the mean of the height and reach columns.
        grouping_by_weight_classes: pd.DataFrame = reach_height_df.groupby(
            "weight_class"
        )[height_reach_cols].mean()

        return grouping_by_weight_classes[height_reach_cols]

    def _handle_height_reach(self) -> None:
        avg_height_reach_df = self.get_height_reach_avgs()
        height_reach_cols: List[str] = self._get_height_reach_cols()
        self._convert_to_cm(self.df, height_reach_cols)

        missing_indices = self.df.index[self.df[height_reach_cols].isna().any(axis=1)]

        for column in height_reach_cols:
            for i in missing_indices:
                if np.isnan(self.df.loc[i, column]):
                    self.df.loc[i, column] = avg_height_reach_df.loc[
                        self.df.loc[i, "weight_class"], column
                    ]

        self._create_height_reach_diff_columns(height_reach_cols)

    def _create_height_reach_diff_columns(self, height_reach_cols):
        height_columns = [height_reach_cols[0], height_reach_cols[2]]
        reach_columns = [height_reach_cols[1], height_reach_cols[3]]

        self.df["height_diff"] = (
            self.df[height_columns[0]] - self.df[height_columns[1]]
        )  # Red height minus Blue height. So positve value suggests red taller, negative implies red shorter.
        self.df["reach_diff"] = (
            self.df[reach_columns[0]] - self.df[reach_columns[1]]
        )  # Same as for height.

    def _convert_reach(self, reach):
        # Convert both reach columns into cm
        try:
            clean_reach = float(reach.replace('"', ""))
            return clean_reach * 2.54
        except ValueError:
            return np.nan

    def _convert_height(self, height: str) -> float:
        """
        Converts a height in feet'inches to centimeters.
        """
        try:
            feet_str, inches_str = height.split("'")
            feet = int(feet_str)
            inches = int(inches_str.replace('"', ""))
            return round((feet * 12 + inches) * 2.54, 0)
        except ValueError:
            return np.nan

    def _convert_to_cm(self, dataframe: pd.DataFrame, height_reach_cols: List[str]):
        for column in height_reach_cols:
            if "height" in column.lower():
                dataframe[column] = dataframe[column].apply(self._convert_height)
            else:
                dataframe[column] = dataframe[column].apply(self._convert_reach)

    def _get_height_reach_cols(self) -> List[str]:
        """
        Extracts the height and reach columns from the dataframe.
        Makes it easier to work with due to red/blue prefixes.
        """
        return [
            column
            for column in self.df.columns
            if "reach" in column.lower() or "height" in column.lower()
        ]
