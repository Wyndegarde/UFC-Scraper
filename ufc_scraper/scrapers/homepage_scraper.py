"""
Module responsible for scraping the details for each event.
"""
from typing import List

from ufc_scraper.base_classes import ScraperABC


class HomepageScraper(ScraperABC):
    """
    Class to scrape the homepage. Will get all the links for each event.
    """

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
        return links

    def scrape_url(self) -> List[str]:
        return self._get_links()
        # return ["http://www.ufcstats.com/event-details/3c6976f8182d9527",
        #         "http://www.ufcstats.com/event-details/51b1e2fd9872005b",
        #         "http://www.ufcstats.com/event-details/6fb1ba67bef41b37",
        #         "http://www.ufcstats.com/event-details/15b1b21cd743d652",
        #         "http://www.ufcstats.com/event-details/3dc3022232b79c7a"]
