from ufc_scraper.processors import FeatureEngineeringProcessor


fe = FeatureEngineeringProcessor(
    csv_path="ufc_scraper/data/clean_ufc_data.csv", allow_creation=True
)
fe.run_feature_engineering()