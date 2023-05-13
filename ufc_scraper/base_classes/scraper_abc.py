"""
This script contains the abstract base class for all scrapers.
Each page type has its own scraper class, which inherits from this class.
the ABC contains all methods that are common to all scrapers.
"""

from typing import Dict, Union, List, Optional
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup


class ScraperABC(ABC):
    """
    Abstract base class for all scrapers.
    """

    def __init__(self, url: str) -> None:
        """
        Initialises the ScraperABC class.

        Args:
            url (str): URL to scrape.
        """
        self.url = url
        self.red_prefix = "red_"
        self.blue_prefix = "blue_"

    def _get_soup(
        self, params: Optional[Dict[str, Union[str, int]]] = None
    ) -> BeautifulSoup:
        """
        Method to get the soup for a given URL.

        Args:
            params (Optional[Dict[str, Union[str, int]]], optional): params dict for making a reques. Defaults to None.

        Returns:
            BeautifulSoup: Soup object for the given URL.
        """
        response = requests.get(self.url, timeout=100, params=params)
        soup: BeautifulSoup = BeautifulSoup(response.text, "lxml")
        return soup

    def _clean_text(self, text: str) -> str:
        """
        Cleans the text by removing new lines and extra spaces.

        Args:
            text (str): scraped text, usually an html tag.

        Returns:
            str: cleaned text.
        """
        clean_text: str = text.strip().replace("\n", "").replace("    ", "")
        return clean_text

    def _apply_rb_prefix(self, text: Union[List[str], str]) -> List[str]:
        """
        adds the corner colour prefix to the text.

        Args:
            text (Union[List[str], str]): either a list of strings or a single string.

        Returns:
            List[str]: a list of strings with the prefix applied to each entry.
        """

        if isinstance(text, list):
            return [
                self.red_prefix + entry if i % 2 == 0 else self.blue_prefix + entry
                for i, entry in enumerate(text)
            ]
        elif isinstance(text, str):
            return [self.red_prefix + text, self.blue_prefix + text]

    @abstractmethod
    def scrape_url(self):
        """
        Abstract method to scrape the URL.
        All subclasses must implement this method to execute the logic for scraping their URL.
        """
