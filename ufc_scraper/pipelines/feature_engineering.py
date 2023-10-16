from ufc_scraper.config import PathSettings
from ufc_scraper.feature_engineering import FeatureEngineering


class FeatureEngineeringPipeline:
    def run_pipeline(self):
        feature_engineering = FeatureEngineering(
            csv_path=PathSettings.CLEAN_DATA_CSV, allow_creation=False
        )

        feature_engineering.run_feature_engineering()