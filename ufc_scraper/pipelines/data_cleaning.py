"""
This script is respoonsible for taking in the scraped data and ceaning it for use in the model.
"""

from ufc_scraper.processors import DataProcessor
from ufc_scraper.config import PathSettings

class DataCleaningPipeline:
               
    def run_pipeline(self):
        cleaning_processor = DataProcessor(
            csv_path= PathSettings.RAW_DATA_CSV,
            allow_creation=False)
        
        cleaning_processor.clean_raw_data()