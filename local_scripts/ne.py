from src.lib.pipelines import ScrapingPipeline
from src.config import PathSettings
import asyncio


async def main():
    # create data dir if it doesnt exist
    PathSettings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    scraping_pipeline = ScrapingPipeline()
    await scraping_pipeline.scrape_next_event()


if __name__ == "__main__":
    asyncio.run(main())
