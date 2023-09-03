from abc import ABC
from pathlib import Path

import pandas as pd


class DataFrameABC(ABC):
    """
    Abstract class to handle the loading and writing of dataframes.
    """

    def __init__(self, csv_path: Path, allow_creation: bool = False) -> None:
        self.csv_path: Path = csv_path
        self.allow_creation: bool = allow_creation
        self.object_df: pd.DataFrame = self._instantiate_df()

    def _instantiate_df(self) -> pd.DataFrame:
        """
        Method to load the csv file into a dataframe.
        Handles cases where file does not exist with two options:
        1. If allow_creation is True, creates an empty dataframe. For cases where the existance of the file is not necessary.
        2. If allow_creation is False, raises a FileNotFoundError. For cases where the existance of the file is necessary.

        Raises:
            FileNotFoundError: If the file does not exist and we require it to.

        Returns:
            pd.DataFrame: the csv file as a dataframe (or the newly created empty dataframe)
        """
        try:
            data_frame: pd.DataFrame = pd.read_csv(self.csv_path)
        except FileNotFoundError as exc:
            if self.allow_creation:
                data_frame = pd.DataFrame()
            else:
                raise FileNotFoundError(
                    "File does not exist and allow_creation is False,\
                          check input path or for other errors."
                ) from exc
        return data_frame

    def add_row(self, row_to_add: pd.DataFrame) -> None:
        self.object_df = pd.concat([self.object_df, row_to_add], ignore_index=True)

    def write_csv(self) -> None:
        """
        Method to write the dataframe to a csv file.
        """
        self.object_df.to_csv(self.csv_path, index=False)
