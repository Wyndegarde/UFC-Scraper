import pandas as pd

from ufc_scraper.base_classes import DataFrameABC


class RawDataProcessor(DataFrameABC):
    def __init__(self, csv_path: str, allow_creation: bool = False) -> None:
        super().__init__(csv_path, allow_creation)

        print(self.csv_path)

    def add_row(self, row_to_add: pd.DataFrame) -> None:
        self.object_df = pd.concat([self.object_df, row_to_add], ignore_index=True)
