"""
Class to scrape a single event.
"""
from typing import List

from ufc_scraper.base_classes import ScraperABC


class CardScraper(ScraperABC):
    """
    Class to scrape a single event.
    """

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.ufc_card = self._get_soup()

    def _get_event_details(self):
        event_info = (
            self.ufc_card.find(class_="b-list__box-list")
            .text.replace("\n", "")
            .split("      ")
        )
        # Gets the Date and Location.
        date = event_info[3]
        location = event_info[-1]

        return (date, location)

    def _get_fight_links(self) -> List[str]:
        fight_links: List[str] = []
        for tag in self.ufc_card.find_all():
            link_to_fight = tag.get("data-link")
            if link_to_fight and "fight-details" in link_to_fight:
                fight_links.append(link_to_fight)

        return fight_links

    def scrape_url(self):
        ...
