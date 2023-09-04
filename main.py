from ufc_scraper.pipelines import ScrapingPipeline, DataCleaningPipeline
from ufc_scraper.feature_engineering import FeatureEngineeringProcessor
from ufc_scraper.config import PathSettings

def main():
    scraping_pipeline = ScrapingPipeline()
    scraping_pipeline.run_pipeline()
    data_cleaning = DataCleaningPipeline()
    data_cleaning.run_pipeline()
    feature_engineering = FeatureEngineeringProcessor(csv_path = PathSettings.CLEAN_DATA_CSV, allow_creation = False)
    feature_engineering.run_feature_engineering()

if __name__ == "__main__":
    main()
