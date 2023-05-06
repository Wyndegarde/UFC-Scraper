from typing import Dict, Union
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

class ScraperABC(ABC):
    def __init__(self, url):
        self.url = url

    def _get_soup(self, params: Dict[str, Union[str,int]] = {}, **kwargs):
        response = requests.get(self.url, timeout=100, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        return soup

    def _clean_text(self, text: str) -> str:

        text = text.strip().replace('\n','').replace("    ",'')
        return text
    
    @abstractmethod
    def scrape_url(self):
        pass
