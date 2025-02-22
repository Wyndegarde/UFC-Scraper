from typing import List
import pandas as pd
import numpy as np
from .abstract import CleanerABC


class HeightReachCleaner(CleanerABC):
    # Class constants
    INCHES_TO_CM: float = 2.54
    FEET_TO_INCHES: int = 12

    def clean(self) -> pd.DataFrame:
        """
        Cleans height and reach data by converting measurements to centimeters,
        handling missing values, and creating difference columns.

        This method:
        1. Converts all height/reach measurements to centimeters
        2. Fills missing values using weight class averages
        3. Creates columns for height and reach differences between fighters
        """
        height_reach_cols: List[str] = self._get_height_reach_cols()

        self._convert_to_cm(height_reach_cols)
        self._fill_missing_measurements(height_reach_cols)
        self._create_measurement_differences(height_reach_cols)
        return self.df

    def _get_height_reach_cols(self) -> List[str]:
        """
        Extracts the height and reach column names from the dataframe.

        Returns:
            List[str]: A list of column names containing height and reach measurements
        """

        height_cols: List[str] = [
            col for col in self.df.columns if "height" in col.lower()
        ]
        reach_cols: List[str] = [
            col for col in self.df.columns if "reach" in col.lower()
        ]
        return height_cols + reach_cols

    def _create_height_reach_avgs(self) -> pd.DataFrame:
        """
        Calculates average height and reach measurements grouped by weight class.

        Returns:
            pd.DataFrame: DataFrame containing mean height and reach measurements
                for each weight class. Index is weight class, columns are
                height and reach measurements.
        """
        height_reach_cols: List[str] = self._get_height_reach_cols()

        clean_df: pd.DataFrame = self.df.copy()
        clean_df.dropna(subset=height_reach_cols, inplace=True)
        self._convert_to_cm(height_reach_cols)

        return clean_df.groupby("weight_class")[height_reach_cols].mean()

    def _fill_missing_measurements(self, height_reach_cols: List[str]) -> None:
        """
        Fills missing height and reach values using weight class averages.

        Args:
            height_reach_cols (List[str]): List of column names containing
                height and reach measurements to be filled
        """
        avg_measurements: pd.DataFrame = self._create_height_reach_avgs()
        missing_mask: pd.Series = self.df[height_reach_cols].isna().any(axis=1)
        missing_indices: pd.Index = self.df.index[missing_mask]

        for col in height_reach_cols:
            for idx in missing_indices:
                if np.isnan(self.df.loc[idx, col]):
                    weight_class: str = self.df.loc[idx, "weight_class"]
                    self.df.loc[idx, col] = avg_measurements.loc[weight_class, col]

    def _create_measurement_differences(self, height_reach_cols: List[str]) -> None:
        """
        Creates columns for height and reach differences between fighters.

        Calculates the difference between fighters' measurements and stores
        them in 'height_diff' and 'reach_diff' columns.

        Args:
            height_reach_cols (List[str]): List of column names containing
                height and reach measurements
        """
        self.df["height_diff"] = (
            self.df[height_reach_cols[0]] - self.df[height_reach_cols[1]]
        )
        self.df["reach_diff"] = (
            self.df[height_reach_cols[2]] - self.df[height_reach_cols[3]]
        )

    def _convert_reach(self, reach: str) -> float:
        """
        Converts reach measurement from inches to centimeters.

        Args:
            reach (str): Reach measurement in inches (e.g., '72"')

        Returns:
            float: Reach measurement in centimeters, or np.nan if conversion fails
        """
        try:
            inches: float = float(reach.replace('"', ""))
            return inches * self.INCHES_TO_CM
        except (ValueError, AttributeError):
            return np.nan

    def _convert_height(self, height: str) -> float:
        """
        Converts height from feet'inches format to centimeters.

        Args:
            height (str): Height in feet'inches format (e.g., "5'11")

        Returns:
            float: Height in centimeters, rounded to nearest integer,
                or np.nan if conversion fails
        """
        try:
            feet_str: str
            inches_str: str
            feet_str, inches_str = height.split("'")
            feet: int = int(feet_str)
            inches: int = int(inches_str.replace('"', ""))
            total_cm: float = (feet * self.FEET_TO_INCHES + inches) * self.INCHES_TO_CM
            return round(total_cm, 0)
        except (ValueError, AttributeError):
            return np.nan

    def _convert_to_cm(self, height_reach_cols: List[str]) -> None:
        """
        Converts all height and reach measurements to centimeters.

        Args:
            height_reach_cols (List[str]): List of column names containing
                height and reach measurements to be converted
        """
        for column in height_reach_cols:
            if "height" in column.lower():
                self.df[column] = self.df[column].apply(self._convert_height)
            else:
                self.df[column] = self.df[column].apply(self._convert_reach)
