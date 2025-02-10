from django.http import HttpResponse
from src.config.config import PathSettings
from src.lib.engines import ScrapingEngine
from src.lib.pipelines import ScrapingPipeline
from src.lib.processing import JSONCache, CSVProcessingHandler


async def scrape_past_events(request):
    scraping_pipeline = ScrapingPipeline(
        ScrapingEngine(),
        JSONCache(PathSettings.EVENT_CACHE_JSON),
    )
    raw_data_processor = CSVProcessingHandler(
        PathSettings.RAW_DATA_CSV, allow_creation=True
    )
    await scraping_pipeline.run(raw_data_processor)
    return HttpResponse("Scraping past events")
