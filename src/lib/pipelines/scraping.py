import asyncio
from typing import Dict, Any, List
from pathlib import Path

import pandas as pd

from src.lib.data_cleaning import DataCleaner
from src.lib.engines import ScrapingEngine
from src.lib.exceptions import ScrapingException
from src.lib.processing import ProcessingHandlerABC
from src.lib.processing.cache import CacheABC
from src.lib.scrapers import (
    HomepageScraper,
    BoutScraper,
    CardScraper,
)
from src.config import PathSettings, console


class ScrapingPipeline:
    """
    Runs the pipeline to scrape the UFC stats data
    """

    # Limit the number of concurrent tasks
    sem = asyncio.Semaphore(10)

    def __init__(self, scraping_engine: ScrapingEngine, cache: CacheABC) -> None:
        self.scraping_engine = scraping_engine
        self.cache = cache

    async def run(self, raw_data_processor: ProcessingHandlerABC) -> None:
        """
        Executes all the logic from the scrapers and writes the data to the csv files.
        """

        cached_event_links: List[str] = self.cache.get()

        # Instantiate the homepage scraper and get all the links to each event.
        homepage = HomepageScraper(
            url="http://www.ufcstats.com/statistics/events/completed",
            cache=cached_event_links,
        )

        filtered_event_links: List[str] = await homepage.scrape_url()

        results = await self._scrape_events(
            filtered_event_links,
            homepage,
            raw_data_processor,
        )

        for result in results:
            if isinstance(result, ScrapingException):
                console.log(result)

        self.cache.write(homepage.cache)
        raw_data_processor.write()

    async def _scrape_events(
        self,
        filtered_event_links: List[str],
        homepage: HomepageScraper,
        raw_data_processor: ProcessingHandlerABC,
    ) -> List[Any]:
        """
        Asynchronously scrapes the events in batches of 10.
        Creates a task for each event and adds it to the list of tasks.
        """
        tasks = []
        batch = []
        batch_size = 10
        for link_to_event in filtered_event_links:
            batch.append(link_to_event)
            if len(batch) == batch_size:
                for link in batch:
                    tasks.append(
                        asyncio.create_task(
                            self.scrape_card_task(link, homepage, raw_data_processor)
                        )
                    )
                # Sleep for 1 second to avoid rate limiting
                await asyncio.sleep(1)
                batch = []

        if batch:
            for link in batch:
                tasks.append(
                    asyncio.create_task(
                        self.scrape_card_task(link, homepage, raw_data_processor)
                    )
                )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return results

    async def scrape_card_task(
        self,
        link_to_event: str,
        homepage: HomepageScraper,
        raw_data_processor: ProcessingHandlerABC,
    ) -> None:
        async with self.sem:
            try:
                full_fight_details: Dict[str, str] = (
                    await self.scraping_engine.scrape_card(link_to_event, homepage)
                )
                raw_data_processor.add_row(full_fight_details)
            except Exception as e:
                console.log(f"Failed to scrape {link_to_event}")
                console.log(e)
                raise ScrapingException(f"Failed to scrape {link_to_event}")

    async def scrape_next_event(self) -> None:
        # Removes the existing next event (if it exists)
        existing_future_event = Path(PathSettings.NEXT_EVENT_CSV)
        existing_future_event.unlink(missing_ok=True)

        # Creates the next event object for cleaning and writing the csv
        next_event_processor = DataCleaner(
            csv_path=PathSettings.NEXT_EVENT_CSV, allow_creation=True
        )

        cache = self.cache.get()
        homepage = HomepageScraper(
            url="http://www.ufcstats.com/statistics/events/completed",
            cache=cache,
        )
        # Returns the link to the next event - different tag to previous events.
        next_event_link = await homepage._get_next_event()

        fight_card = CardScraper(next_event_link)
        event_name, date, location, fight_links = await fight_card.scrape_url()

        fight_links = list(set(fight_links))
        self.scraping_engine._display_event_details(
            event_name, date, location, fight_links
        )

        for fight in fight_links:
            bout = BoutScraper(url=fight, date=date, location=location)
            fight_ = await bout._aget_soup()
            fighter_links = bout.get_fighter_links(fight=fight_)
            fighter_profiles = await self.scraping_engine.scrape_fighter(fighter_links)

            all_info = await bout.extract_future_bout_stats()

            full_fight_details = {**all_info, **fighter_profiles}
            full_fight_details_df = pd.DataFrame.from_dict(
                full_fight_details, orient="index"
            ).T
        next_event_processor.add_row(full_fight_details_df)

        next_event_processor.clean_next_event()
        next_event_processor.write()
