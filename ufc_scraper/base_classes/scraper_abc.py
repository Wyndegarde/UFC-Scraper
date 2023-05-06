from typing import Dict
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup


class ScraperABC(ABC):
    def __init__(self, url):
        self.url = url

    def _get_soup(self, params: Dict[str, str] = {}, **kwargs):
        response = requests.get(self.url, timeout=100, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        return soup

    @abstractmethod
    def scrape_url(self):
        pass
