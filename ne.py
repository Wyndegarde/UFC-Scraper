from ufc_scraper.pipelines import ScrapingPipeline
from ufc_scraper.config import PathSettings

if __name__ == "__main__":
    PathSettings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    scraper = ScrapingPipeline()
    scraper.scrape_next_event()
