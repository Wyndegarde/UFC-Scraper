"""
Class to scrape a single event.
"""

import requests
from bs4 import BeautifulSoup

from ufc_scraper.base_classes import ScraperABC


class EventScrapper(ScraperABC):
    def _get_event_details(self):
        ufc_card = self._get_soup()

        event_info = (
            ufc_card.find(class_="b-list__box-list")
            .text.replace("\n", "")
            .split("      ")
        )
        # Gets the Date and Location.
        date = event_info[3]
        location = event_info[-1]

        return (date, location)

    def _get_fighter_links(self):
        ufc_card = self._get_soup()

        fighter_links = []
        for link in ufc_card.find_all(
            "a", class_="b-link b-link_style_black", href=True
        ):
            fighter_links.append(link["href"])
        return fighter_links

    def scrape_url(self):
        ...
