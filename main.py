from ufc_scraper.pipelines import ScrapingPipeline


def main():
    scraping_pipeline = ScrapingPipeline()
    scraping_pipeline.run_pipeline()


if __name__ == "__main__":
    main()
