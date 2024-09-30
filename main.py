from ufc_scraper.pipelines import ScrapingPipeline, DataCleaningPipeline
from ufc_scraper.feature_engineering import FeatureEngineering
from ufc_scraper.config import PathSettings

import asyncio


async def main():
    # create data dir if it doesnt exist
    PathSettings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    scraping_pipeline = ScrapingPipeline()
    await scraping_pipeline.run_pipeline()
    # data_cleaning = DataCleaningPipeline()
    # data_cleaning.run_pipeline()
    # feature_engineering = FeatureEngineering(
    #     csv_path=PathSettings.CLEAN_DATA_CSV, allow_creation=False
    # )
    # feature_engineering.run_feature_engineering()


if __name__ == "__main__":
    asyncio.run(main())
