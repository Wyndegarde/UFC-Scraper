"""
This script is respoonsible for taking in the scraped data and ceaning it for use in the model.
"""

from src.lib.engines.data_cleaning import DataCleaningEngine
from src.config import PathSettings


class DataCleaningPipeline:
    def run(self):
        data_cleaner = DataCleaningEngine(
            csv_path=PathSettings.RAW_DATA_CSV, allow_creation=False
        )

        data_cleaner.clean_raw_data()
