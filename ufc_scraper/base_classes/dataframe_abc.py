from abc import ABC
import pandas as pd


class DataFrameABC(ABC):
    def __init__(self, csv_path: str, allow_creation: bool = False) -> None:
        self.csv_path = csv_path
        self.allow_creation = allow_creation
        self.df = self._instantiate_df()

    def _instantiate_df(self) -> pd.DataFrame:
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
