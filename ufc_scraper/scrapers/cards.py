"""
Class to scrape a single event.
"""
from typing import List, Tuple

from ufc_scraper.base_classes import ScraperABC


class CardScraper(ScraperABC):
    """
    Class to scrape a single event.
    """

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.ufc_card = self._get_soup()

    def _extract_event_name(self) -> str:
        """
        Responsible for extracting the event name of the card.

        Returns:
            str: The event name
        """
        event_name: str = self.ufc_card.find(class_="b-content__title-highlight").text  # type: ignore
        return event_name.strip()

    def _extract_event_details(self) -> Tuple[str, str]:
        """
        Gets the date and location of the event.

        Returns:
            Tuple[str,str]: the date and location of the event.
        """
        event_info = (
            self.ufc_card.find(class_="b-list__box-list")  # type: ignore
            .text.replace("\n", "")
            .split("      ")
        )  # type: ignore

        # Gets the Date and Location.
        date: str = event_info[3].strip()
        location: str = event_info[-1].strip()

        return (date, location)

    def _extract_fight_links(self) -> List[str]:
        """
        Extracts all the links to the fights on the card.

        Returns:
            List[str]: List of urls to each fight on the card.
        """
        fight_links: List[str] = []
        for tag in self.ufc_card.find_all():
            link_to_fight = tag.get("data-link")
            if link_to_fight and "fight-details" in link_to_fight:
                fight_links.append(link_to_fight)

        return fight_links

    def scrape_url(self) -> Tuple[str, str, str, List[str]]:
        """
        Executes all the logic to get the information about a single event.
        """
        event_name: str = self._extract_event_name()
        date, location = self._extract_event_details()
        fight_links: List[str] = self._extract_fight_links()

        return event_name, date, location, fight_links
