"""
Module responsible for cleaning the raw data scraped from the web.
"""

from pathlib import Path

from src.lib.processing import CSVProcessingHandler
from src.config import PathSettings
from src.lib.preprocessing.constants import UFC_KEY_COLUMNS
from src.lib.preprocessing.cleaners import (
    CoreCleaner,
    DateCleaner,
    HeightReachCleaner,
    StatsCleaner,
)


class DataCleaningEngine(CSVProcessingHandler):
    """
    Reads in the raw data scraped from the web and cleans it.

    Args:
        CSVProcessingHandler: Class containing functionality for all csv data.
    """

    def __init__(self, csv_path: Path, allow_creation: bool = False) -> None:
        super().__init__(csv_path, allow_creation)

        # Additional flag for where an error occurs during scraping and data isn't saved
        if (not allow_creation) and (self.df.empty):
            raise ValueError("DataFrame must not be empty")

    def clean_raw_data(self):
        self.df = CoreCleaner(self.df).clean()
        self.df = DateCleaner(self.df).clean()
        self.df = HeightReachCleaner(self.df).clean()
        self.df = StatsCleaner(self.df).clean()

        # Using only the columns necessary for the model training.
        self.df = self.df[UFC_KEY_COLUMNS]
        self.df.to_csv(PathSettings.CLEAN_DATA_CSV, index=False)

    def clean_next_event(self):

        self.df = StatsCleaner(self.df).clean_next_event()
        self.df = CoreCleaner(self.df).clean_next_event()
        self.df = HeightReachCleaner(self.df).clean_next_event()
        self.df.to_csv(PathSettings.NEXT_EVENT_CSV, index=False)

    def get_fights_per_fighter(self):
        return self.df["red_fighter"].append(self.df["blue_fighter"]).value_counts()
