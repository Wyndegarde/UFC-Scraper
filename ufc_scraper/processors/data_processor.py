from pathlib import Path
from ufc_scraper.base_classes import DataFrameABC


class DataProcessor(DataFrameABC):
    def __init__(self, csv_path: Path, allow_creation: bool = False) -> None:
        super().__init__(csv_path, allow_creation)


