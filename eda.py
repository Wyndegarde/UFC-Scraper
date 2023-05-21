import pandas as pd

from ufc_scraper.config import PathSettings
from ufc_scraper.data_processing import DataCleaningHandler

ufc_df = pd.read_csv(PathSettings.RAW_DATA_CSV)
print(ufc_df.columns)
print(ufc_df.head())

data_cleaning_handler = DataCleaningHandler(PathSettings.RAW_DATA_CSV)

data_cleaning_handler.run_pipeline()
