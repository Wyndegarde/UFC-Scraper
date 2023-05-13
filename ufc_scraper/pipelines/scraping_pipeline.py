from typing import Dict, Any, List

from rich.progress import track
from rich.console import Console

import pandas as pd

from ufc_scraper.data_processing import RawDataProcessor, CacheProcessor
from ufc_scraper.scrapers import (
    HomepageScraper,
    BoutScraper,
    FighterScraper,
    CardScraper,
)
from ufc_scraper.config import PathSettings

console = Console()
import time

from rich.progress import Progress

# with Progress() as progress:

#     fight_task = progress.add_task("[red]Scraping Fights...", total=1000)
#     task2 = progress.add_task("[green]Processing...", total=1000)
#     task3 = progress.add_task("[cyan]Cooking...", total=1000)

class ScrapingPipeline:
    """
    Runs the pipeline to scrape the UFC stats data

    #! NOTE: This is just a copilot suggestion for now - need to refine.
    #! Added so there was a starting point.
    """

    def _extract_fighter_profiles(self, fighter_links: List[str]) -> Dict[str, str]:
        red_fighter = FighterScraper(fighter_links[0], red_corner=True)
        blue_fighter = FighterScraper(fighter_links[1], red_corner=False)

        red_fighter_profile: Dict[str, str] = red_fighter.scrape_url()
        blue_fighter_profile: Dict[str, str] = blue_fighter.scrape_url()

        fighter_profiles: Dict[str, str] = {
            **red_fighter_profile,
            **blue_fighter_profile,
        }

        return fighter_profiles

    def run_pipeline(self) -> Any:
        console.rule("", style = "black")
        raw_data_processor = RawDataProcessor(
            csv_path=PathSettings.RAW_DATA_CSV, allow_creation=True
        )
        event_cache = CacheProcessor(
            csv_path=PathSettings.EVENT_CACHE_CSV,
            cache_column_name="event_link",
            allow_creation=True,
        )

        homepage = HomepageScraper(
            "http://www.ufcstats.com/statistics/events/completed"
        )

        all_event_links: List[str] = homepage.scrape_url()

        for link_to_event in all_event_links:
            # if event_cache.check_cache(link_to_event):
            #     print(f"Skipping {link_to_event} as it has already been scraped.")
            #     continue
            fight_card = CardScraper(link_to_event)
            date, location = fight_card.get_event_details()
            fight_links = fight_card.get_fight_links()
            event_name = fight_card.ufc_card.find(class_="b-content__title-highlight").text.strip() # type: ignore
            console.rule(f"[bold white]Scraping {event_name}", style = "bold magenta")
            with Progress() as progress:

                fight_task = progress.add_task("[red]Scraping Fights...", total=len(fight_links), style = "green")
                fighter_profile_task = progress.add_task("[blue]Scraping fighter profiles...", total=len(fight_links)*2)
                for fight in fight_links:
                    bout = BoutScraper(url=fight, date=date, location=location)
                    full_bout_details, fighter_links = bout.scrape_url()

                    assert len(fighter_links) >= 2, "There should be two fighters per bout."

                    fighter_profiles: Dict[str, str] = self._extract_fighter_profiles(
                        fighter_links
                    )

                    full_fight_details: Dict[str, str] = {
                        **full_bout_details,
                        **fighter_profiles,
                    }

                    full_fight_details_df = pd.DataFrame.from_dict(
                        full_fight_details, orient="index"
                    ).T

                    raw_data_processor.add_row(full_fight_details_df)
                    # console.log(f"\nFinished scraping fight")
                    progress.update(fight_task, advance=1)
                    progress.update(fighter_profile_task, advance=2)

            console.rule("", style = "black")
            link_to_event_df = pd.DataFrame.from_dict(
                {"event_link": link_to_event}, orient="index"
            ).T
            event_cache.add_row(link_to_event_df)

            # raw_data_processor.write_csv()
            # event_cache.write_csv()
            # console.log(f"Finished scraping {link_to_event}", log_locals=True)
