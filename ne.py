
from ufc_scraper.pipelines import ScrapingPipeline

if __name__ == "__main__":
    scraper = ScrapingPipeline()
    scraper.scrape_next_event()
    