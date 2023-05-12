"""
Module for scraping the information for each fighter from their stats page.
"""
from typing import Dict, List
from ufc_scraper.base_classes import ScraperABC


class FighterScraper(ScraperABC):

    """
    Class to scrape the information for each fighter from their stats page.
    """

    def __init__(self, url: str):
        """
        Instantiates the class and calls the parent class to get the soup object.

        Args:
            url (str): URL for a single fighters profile.
        """
        super().__init__(url)
        self.fighter = self._get_soup()

    def get_figther_details(self) -> Dict[str, str]:
        """
        Generates a dictionary containing all of the information for a single fighter.

        Returns:
            Dict[str, str]: fighter information. key = name of stat, value = stat.
        """

        # First find their record.
        record = self.fighter.find(class_="b-content__title-record")

        # Strip it down and add it to the list - results in ["Record", "Ws-Ls-Ds" (x Ncs)"]
        # ? Ncs is number of no contests. unsure if included if x=0.
        cleaned_record = self._clean_text(record.text).split(":")  # type: ignore

        # Next we go through all of the summary stats for each fighter.
        career_info = self.fighter.find_all(
            class_="b-list__box-list-item b-list__box-list-item_type_block"
        )
        all_info = []  # Create a list to store all of the info for each fighter.

        for each in career_info:
            # Each entry is a 2 element list containing the name of the stat and the stat itself.
            # clean text then split on the colon.
            output: List[str] = self._clean_text(each.text).split(":")

            # Add the info for each fighter to the list.
            all_info.append(output)

        # Create a dictionary using the stat name and the stat.
        fighter_profile: Dict[str, str] = {
            entry[0]: entry[1] for entry in all_info if len(entry) == 2
        }
        fighter_profile["Record"] = cleaned_record[1]
        return fighter_profile

    def scrape_url(self):
        ...
