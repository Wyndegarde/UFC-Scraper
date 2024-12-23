"""
This script is respoonsible for taking in the scraped data and ceaning it for use in the model.
"""

from src.lib.data_cleaning import DataCleaner
from src.config import PathSettings


class DataCleaningPipeline:
    def run(self):
        data_cleaner = DataCleaner(
            csv_path=PathSettings.RAW_DATA_CSV, allow_creation=False
        )

        data_cleaner.clean_raw_data()
