from typing import Dict, Union, List
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
    
    def _apply_rb_prefix(self, text: Union[List[str],str]) -> List[str]:
        red_prefix = "red_"
        blue_prefix = "blue_"

        if isinstance(text, list):
            return [red_prefix + entry if i % 2 == 0 else blue_prefix + entry for i, entry in enumerate(text)]
        elif isinstance(text, str):
            return [red_prefix + text, blue_prefix + text]


    @abstractmethod
    def scrape_url(self):
        pass
