from bs4 import BeautifulSoup

from ufc_scraper.config import PathSettings
from ufc_scraper.scrapers import FighterScraper
#! This is a temp implementation for now, just to learn monkeypatching.
def test_fighter(monkeypatch):
    def tmp_soup(self):
        with open(PathSettings.TEST_FIGHTER_PROFILE, "r") as f:
            html = f.read()
        return BeautifulSoup(html, "lxml")
    
    monkeypatch.setattr(FighterScraper, "_get_soup", tmp_soup)

    fighter = FighterScraper(url = "dummy", red_corner = True)
    
    expected_record = ["Record", " 24-2-0"]

    assert fighter._extract_fighter_record() == expected_record