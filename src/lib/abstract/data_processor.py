from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

import pandas as pd


class DataProcessorABC(ABC):
    pd

    @abstractmethod
    def instantiate(self, *args, **kwargs):
        """
        Instantiates the data processor.
        """
        pass

    @abstractmethod
    def add_row(self, *args, **kwargs):
        """
        Adds a row to the data processor.
        """
        pass

    @abstractmethod
    def write(self, *args, **kwargs):
        """
        Writes the data processor to a file.
        """
        pass


class CSVDataProcessor(DataProcessorABC):
    def __init__(self, csv_path: Path, allow_creation: bool = False):
        self.csv_path = csv_path
        self.df = self.instantiate()
        self.allow_creation = allow_creation

    def instantiate(self) -> pd.DataFrame:
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
            df: pd.DataFrame = pd.read_csv(self.csv_path)
        except FileNotFoundError as exc:
            if self.allow_creation:
                df = pd.DataFrame()
            else:
                raise FileNotFoundError(
                    "File does not exist and allow_creation is False,\
                          check input path or for other errors."
                ) from exc
        return df

    def add_row(self, row: Dict[str, str]):
        """
        Adds a row to the dataframe.
        """
        row_df = pd.DataFrame.from_dict(row, orient="index").T
        self.df = pd.concat([self.df, row_df], ignore_index=True)

    def write(self):
        """
        Method to write the dataframe to a csv file.
        """
        self.df.to_csv(self.csv_path, index=False)
