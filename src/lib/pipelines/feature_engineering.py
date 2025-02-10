from src.config import PathSettings
from src.lib.feature_engineering import FeatureEngineering


class FeatureEngineeringPipeline:
    def run(self):
        feature_engineering = FeatureEngineering(
            csv_path=PathSettings.CLEAN_DATA_CSV, allow_creation=False
        )

        feature_engineering.run()
