from pathlib import Path

from ufc_scraper.config import PathSettings

print(Path(__file__).parent)
print(PathSettings.BASE_DIR)
print(PathSettings.RAW_DATA_CSV)
