from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from src.lib.pipelines import ScrapingPipeline


async def scrape_past_events(request):
    scraping_pipeline = ScrapingPipeline()
    await scraping_pipeline.run()
    return HttpResponse("Scraping past events")
