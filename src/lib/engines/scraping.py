from typing import List, Dict
from rich.console import Console

from src.lib.exceptions import ScrapingException
from src.lib.processing.handlers import ProcessingHandlerABC
from src.lib.scrapers import CardScraper, BoutScraper, FighterScraper

console = Console()


class ScrapingEngine:
    def __init__(self):
        pass

    def run(self, link_to_event, homepage):
        try:
            return self.scrape_card(link_to_event, homepage)
        except ScrapingException as e:
            console.log(e)
            raise e

    async def scrape_card(
        self,
        link_to_event,
        homepage,
        raw_data_processor: ProcessingHandlerABC,
    ):
        # Instantiate the card scraper and get the event details.
        fight_card = CardScraper(link_to_event)
        event_name, date, location, fight_links = await fight_card.scrape_url()

        self._display_event_details(event_name, date, location, fight_links)

        # Iterate through each fight on the card and scrape the data.

        for fight in fight_links:
            try:
                full_fight_details = await self.scrape_fight(fight, date, location)
                raw_data_processor.add_row(full_fight_details)
            except Exception:
                raise ScrapingException(f"Failed to scrape {fight}")

        console.rule("", style="black")
        homepage.cache.append(link_to_event)
        console.log(f"Finished scraping {link_to_event}")

    async def scrape_fight(
        self, fight: str, date: str, location: str
    ) -> Dict[str, str]:
        bout: BoutScraper = BoutScraper(url=fight, date=date, location=location)
        try:
            full_bout_details, fighter_links = await bout.scrape_url()

            fighter_profiles: Dict[str, str] = await self.scrape_fighter(fighter_links)
        except Exception:
            raise ScrapingException(f"Failed to scrape {fight}")

        full_fight_details: Dict[str, str] = {
            **full_bout_details,
            **fighter_profiles,
        }
        return full_fight_details

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

    async def scrape_fighter(self, fighter_links: List[str]) -> Dict[str, str]:
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
        red_fighter_profile: Dict[str, str] = await red_fighter.scrape_url()
        blue_fighter_profile: Dict[str, str] = await blue_fighter.scrape_url()

        # Combine the two dictionaries into one.
        fighter_profiles: Dict[str, str] = {
            **red_fighter_profile,
            **blue_fighter_profile,
        }

        return fighter_profiles
