from ufc_scraper.base_classes import DataFrameABC


class RawDataProcessor(DataFrameABC):
    def __init__(self, csv_path: str, allow_creation: bool = False) -> None:
        super().__init__(csv_path, allow_creation)
