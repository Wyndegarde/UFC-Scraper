"""
This script is respoonsible for taking in the scraped data and ceaning it for use in the model.
"""

from src.lib.engines.data_cleaning import DataCleaningEngine
from src.config import PathSettings
from src.lib.preprocessing.cleaners import (
    CoreCleaner,
    DateCleaner,
    FighterCleaner,
    HeightReachCleaner,
    StatsCleaner,
)


class DataCleaningPipeline:
    def run(self):
        data_cleaner = DataCleaningEngine(
            csv_path=PathSettings.RAW_DATA_CSV, allow_creation=False
        )
        cleaners = [
            CoreCleaner,
            FighterCleaner,
            DateCleaner,
            HeightReachCleaner,
            StatsCleaner,
        ]
        data_cleaner.clean_raw_data(cleaners)
