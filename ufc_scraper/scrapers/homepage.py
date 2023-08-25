"""
Module responsible for scraping the details for each event.
"""
import json
from pathlib import Path
from typing import List, Set

from ufc_scraper.base_classes import ScraperABC


class HomepageScraper(ScraperABC):
    """
    Class to scrape the homepage. Will get all the links for each event.
    """

    def __init__(self, url: str, cache_file_path: Path) -> None:
        super().__init__(url)
        self.cache_file_path: Path = cache_file_path
        self.cache = self._get_cache()

    def _get_cache(self) -> List[str]:
        try:
            # read cache from json file
            with open(self.cache_file_path, "r") as f:
                cache = json.load(f)
            return cache
        except FileNotFoundError:
            # create cache
            return []

    def _filter_event_links(self, event_links: List[str]) -> List[str]:
        """
        Filters the event links to only those that have not been scraped yet.

        Args:
            event_links (List[str]): List of event links to filter.

        Returns:
            List[str]: List of event links that have not been scraped yet.
        """

        cached_events: Set[str] = set(self.cache)
        event_set: Set[str] = set(event_links)
        filtered_event_links: List[str] = list(event_set - cached_events)

        return filtered_event_links

    def write_cache(self) -> None:
        """
        Writes the cache to a json file.
        """
        with open(self.cache_file_path, "w") as f:
            json.dump(self.cache, f)

    def _get_links(self) -> List[str]:
        """
        Method to get all the links from the homepage across all pages
        """

        #! Placeholder. Need to dynamically get the number of pages.
        sequence: List[int] = list(range(1, 22))
        links: List[str] = []

        # For each page, get the links
        for i in sequence:
            landing_page = self._get_soup(params={"page": i})
            # For each link in each page, go through them
            for link in landing_page.find_all(
                "a", class_="b-link b-link_style_black", href=True
            ):
                links.append(link["href"])

        filtered_links = self._filter_event_links(links)
        return filtered_links

    def _get_next_event(self) -> str:
        """
        Method to get the link for the next event.
        """
        landing_page = self._get_soup()
        next_event_link = landing_page.find_all(class_="b-link b-link_style_white")
        # using find all gets all the links, so we need to get the first one which contains the next event - check.
        return next_event_link[0]["href"]

    def scrape_url(self) -> List[str]:
        return self._get_links()
        # return ["http://www.ufcstats.com/event-details/3c6976f8182d9527",
        #         "http://www.ufcstats.com/event-details/51b1e2fd9872005b",
        #         "http://www.ufcstats.com/event-details/6fb1ba67bef41b37",
        #         "http://www.ufcstats.com/event-details/15b1b21cd743d652",
        #         "http://www.ufcstats.com/event-details/3dc3022232b79c7a"]
