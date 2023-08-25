from ufc_scraper.pipelines import NextEventPipeline

if __name__ == "__main__":
    next_event = NextEventPipeline()
    next_event.scrape_next_event()