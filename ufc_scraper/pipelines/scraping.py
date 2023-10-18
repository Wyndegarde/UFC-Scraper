from typing import Dict, Any, List
from pathlib import Path
from rich.progress import Progress, TimeElapsedColumn

import pandas as pd

from ufc_scraper.data_cleaning import DataCleaner
from ufc_scraper.scrapers import (
    HomepageScraper,
    BoutScraper,
    FighterScraper,
    CardScraper,
)
from ufc_scraper.config import PathSettings, console

# console = Console()


class ScrapingPipeline:
    """
    Runs the pipeline to scrape the UFC stats data
    """

    def _scrape_fighter_profiles(self, fighter_links: List[str]) -> Dict[str, str]:
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

    def _display_event_details(
        self, event_name: str, date: str, location: str, fight_links: List[str]
    ) -> None:
        """
        Prints out the event details to the console using Rich.
        """
        console.rule(f"[bold cyan]{event_name}[/]", style="bold magenta")
        console.print(
            f"Event took place on [bold blue]{date}[/] in [bold blue]{location}[/].",
            justify="center",
        )
        console.print(
            f"[bold blue]{len(fight_links)}[/] fights on the card to scrape.",
            justify="center",
        )

    def _scrape_fight(
        self, fight: str, date: str, location: str, raw_data_processor: DataCleaner
    ) -> None:
        bout: BoutScraper = BoutScraper(url=fight, date=date, location=location)
        full_bout_details, fighter_links = bout.scrape_url()

        fighter_profiles: Dict[str, str] = self._scrape_fighter_profiles(fighter_links)

        full_fight_details: Dict[str, str] = {
            **full_bout_details,
            **fighter_profiles,
        }

        full_fight_details_df = pd.DataFrame.from_dict(
            full_fight_details, orient="index"
        ).T

        # Adds the row to the dataframe containing all fights.
        raw_data_processor.add_row(full_fight_details_df)

    def run_pipeline(self) -> Any:
        """
        Executes all the logic from the scrapers and writes the data to the csv files.

        Returns:
            Any: Still in progress.
        """

        # Instantiate all data processors required for scraping.
        raw_data_processor = DataCleaner(
            csv_path=PathSettings.RAW_DATA_CSV, allow_creation=True
        )

        # Instantiate the homepage scraper and get all the links to each event.
        homepage = HomepageScraper(
            url="http://www.ufcstats.com/statistics/events/completed",
            cache_file_path=PathSettings.EVENT_CACHE_JSON,
        )

        filtered_event_links: List[str] = homepage.scrape_url()
        total_events: int = len(filtered_event_links)
        for index, link_to_event in enumerate(filtered_event_links):
            # Instantiate the card scraper and get the event details.
            fight_card = CardScraper(link_to_event)
            event_name, date, location, fight_links = fight_card.scrape_url()

            self._display_event_details(event_name, date, location, fight_links)

            # Set up Rich progress bar.
            with Progress(
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
                speed_estimate_period=5.0,
            ) as progress:
                fight_task = progress.add_task(
                    "[red]Scraping Fights...", total=len(fight_links)
                )

                # Iterate through each fight on the card and scrape the data.
                for fight in fight_links:
                    self._scrape_fight(fight, date, location, raw_data_processor)
                    progress.update(fight_task, advance=1)

            console.rule("", style="black")
            homepage.cache.append(link_to_event)
            console.log(f"Finished scraping {link_to_event}")

            # write the data every 10 events and at the end. Reduces the risk of losing data while avoiding writing every time
            # TODO: Fix 2nd condition. Cba right now.
            if (index % 10 == 0) or (total_events - index <= 10):
                homepage.write_cache()
                raw_data_processor.write_csv()

    def scrape_next_event(self) -> None:
        # Removes the existing next event (if it exists)
        existing_future_event = Path(PathSettings.NEXT_EVENT_CSV)
        existing_future_event.unlink(missing_ok=True)

        # Creates the next event object for cleaning and writing the csv
        next_event_processor = DataCleaner(
            csv_path=PathSettings.NEXT_EVENT_CSV, allow_creation=True
        )

        homepage = HomepageScraper(
            url="http://www.ufcstats.com/statistics/events/completed",
            cache_file_path=PathSettings.EVENT_CACHE_JSON,
        )
        # Returns the link to the next event - different tag to previous events.
        next_event_link = homepage._get_next_event()

        fight_card = CardScraper(next_event_link)
        event_name, date, location, fight_links = fight_card.scrape_url()

        fight_links = list(set(fight_links))
        self._display_event_details(event_name, date, location, fight_links)

        for fight in fight_links:
            bout = BoutScraper(url=fight, date=date, location=location)
            fighter_links = bout.get_fighter_links()
            fighter_profiles = self._scrape_fighter_profiles(fighter_links)

            all_info = bout.extract_future_bout_stats()

            full_fight_details = {**all_info, **fighter_profiles}
            full_fight_details_df = pd.DataFrame.from_dict(
                full_fight_details, orient="index"
            ).T
            next_event_processor.add_row(full_fight_details_df)

        # next_event_processor.clean_next_event()
        next_event_processor.write_csv()
