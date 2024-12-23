"""
Module for scraping the information for each fighter from their stats page.
"""
from typing import Dict, List
from .abstract import ScraperABC


class FighterScraper(ScraperABC):

    """
    Class to scrape the information for each fighter from their stats page.
    """

    def __init__(self, url: str, red_corner: bool):
        """
        Instantiates the class and calls the parent class to get the soup object.

        Args:
            url (str): URL for a single fighters profile.
        """
        super().__init__(url)
        # self.fighter = self._get_soup()
        self.prefix = self.red_prefix if red_corner else self.blue_prefix

    def _extract_fighter_record(self, fighter) -> List[str]:
        # First find their record.
        record = fighter.find(class_="b-content__title-record")

        # Strip it down and add it to the list - results in ["Record", "Ws-Ls-Ds" (x Ncs)"]
        # ? Ncs is number of no contests. unsure if included if x=0.
        cleaned_record: List[str] = self._clean_text(record.text).split(":")  # type: ignore

        return cleaned_record

    def _extract_fighter_details(self, fighter) -> Dict[str, str]:
        """
        Generates a dictionary containing all of the information for a single fighter.

        Returns:
            Dict[str, str]: fighter information. key = name of stat, value = stat.
        """

        # List where [0] is fluff, [1] is the actual record.
        cleaned_record: List[str] = self._extract_fighter_record(fighter)

        # Next we go through all of the summary stats for each fighter.
        career_info = fighter.find_all(
            class_="b-list__box-list-item b-list__box-list-item_type_block"
        )

        # Create a list to store all of the info for each fighter.
        all_info: List[List[str]] = []

        for each in career_info:
            # Each entry is a 2 element list containing the name of the stat and the stat itself.
            # clean text then split on the colon.
            output: List[str] = self._clean_text(each.text).split(":")

            # Add the info for each fighter to the list.
            all_info.append(output)
        #! check we dont' need to remove entries
        # Create a dictionary using the stat name and the stat.
        fighter_profile: Dict[str, str] = {
            self.prefix + entry[0]: entry[1] for entry in all_info if len(entry) == 2
        }
        fighter_profile[self.prefix + "record"] = cleaned_record[1]
        return fighter_profile

    async def scrape_url(self) -> Dict[str, str]:
        fighter = await self._aget_soup()
        fighter_profile: Dict[str, str] = self._extract_fighter_details(fighter)

        return fighter_profile
