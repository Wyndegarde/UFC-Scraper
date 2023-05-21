from typing import Dict, Any, List

from rich.console import Console
from rich.progress import Progress, TimeElapsedColumn

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


class ScrapingPipeline:
    """
    Runs the pipeline to scrape the UFC stats data
    """

    def _extract_fighter_profiles(self, fighter_links: List[str]) -> Dict[str, str]:
        """
        Method responsible for extracting the fighter profiles from the bout and formating them.

        Args:
            fighter_links (List[str]): URLS to all found fighter profiles

        Returns:
            Dict[str, str]: All extracted info as a dictionary. keys prefixed by corner of each fighter.
        """

        assert len(fighter_links) >= 2, "There should be two fighters per bout."

        # Create object to extract info for each corner.
        red_fighter = FighterScraper(fighter_links[0], red_corner=True)
        blue_fighter = FighterScraper(fighter_links[1], red_corner=False)

        # Scrape the info for each fighter.
        red_fighter_profile: Dict[str, str] = red_fighter.scrape_url()
        blue_fighter_profile: Dict[str, str] = blue_fighter.scrape_url()

        # Combine the two dictionaries into one.
        fighter_profiles: Dict[str, str] = {
            **red_fighter_profile,
            **blue_fighter_profile,
        }

        return fighter_profiles

    def run_pipeline(self) -> Any:
        """
        Executes all the logic from the scrapers and writes the data to the csv files.

        Returns:
            Any: Still in progress.
        """
        console.rule("", style="black")

        # Instantiate all data processors required for scraping.
        raw_data_processor = RawDataProcessor(
            csv_path=PathSettings.RAW_DATA_CSV, allow_creation=True
        )
        event_cache = CacheProcessor(
            csv_path=PathSettings.EVENT_CACHE_CSV,
            cache_column_name="event_link",
            allow_creation=True,
        )

        # Instantiate the homepage scraper and get all the links to each event.
        homepage = HomepageScraper(
            "http://www.ufcstats.com/statistics/events/completed"
        )

        all_event_links: List[str] = homepage.scrape_url()
        filtered_event_links: List[str] = event_cache.filter_cache(all_event_links)
        for link_to_event in filtered_event_links:
            # if event_cache.check_cache(link_to_event):
            #     console.print(
            #         f"Skipping {link_to_event} as it has already been scraped."
            #     )
            #     continue

            # Instantiate the card scraper and get the event details.
            fight_card = CardScraper(link_to_event)
            event_name, date, location, fight_links = fight_card.scrape_url()

            console.rule(f"[bold cyan]{event_name}[/]", style="bold magenta")
            console.print(
                f"Event took place on [bold blue]{date}[/] in [bold blue]{location}[/].",
                justify="center",
            )
            console.print(
                f"[bold blue]{len(fight_links)}[/] fights on the card to scrape.",
                justify="center",
            )
            with Progress(
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
                speed_estimate_period=5.0,
            ) as progress:
                fight_task = progress.add_task(
                    "[red]Scraping Fights...", total=len(fight_links)
                )
                for fight in fight_links:
                    bout = BoutScraper(url=fight, date=date, location=location)
                    full_bout_details, fighter_links = bout.scrape_url()

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
                    progress.update(fight_task, advance=1)

            link_to_event_df = pd.DataFrame.from_dict(
                {"event_link": link_to_event}, orient="index"
            ).T
            event_cache.add_row(link_to_event_df)
            console.rule("", style="black")
            raw_data_processor.write_csv()
            event_cache.write_csv()
            console.log(f"Finished scraping {link_to_event}")
