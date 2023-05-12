"""
Module to get the information for each bout on a card.
"""
import re
from typing import List, Dict, Tuple, Any

from ufc_scraper.base_classes import ScraperABC


class BoutScraper(ScraperABC):
    """
    Class to scrape the information for each bout on a card.
    """

    def __init__(self, url: str) -> None:
        """
        Instantiates the class and calls the parent class to get the soup object.

        Args:
            url (str): URL to a specific bout on a card.
        """
        super().__init__(url)
        self.fight = self._get_soup()

    def _extract_weight(self) -> Tuple[str, str]:
        """
        Extract the weight class in which the bout took place and whether it was a title bout.

        Returns:
            Tuple[str, str]: the weight class and whether it was a title bout.
        """
        weight: str = self.fight.find(class_="b-fight-details__fight-title").text  # type: ignore

        if "Title" in weight:
            title_bout: str = "Y"
        else:
            title_bout = "N"

        cleaned_weight_class: str = (
            self._clean_text(weight).replace(" Bout", "").replace(" Title", "")
        )

        return cleaned_weight_class, title_bout

    def _extract_bout_outcome(self) -> str:
        """
        Returns the outcome of the bout.
        W indicates the red corner won the bout.

        Returns:
            str: outcome of the bout.
        """
        outcome: str = (
            self.fight.find(class_="b-fight-details__person")  # type: ignore
            .find(
                class_="b-fight-details__person-status b-fight-details__person-status_style_gray"
            )
            .text
        )  # type: ignore

        if outcome:
            win: str = self._clean_text(outcome)
        else:
            win = "W"
        return win

    def _get_fight_details(self) -> Any:
        """
        Gets the fight details for each bout.
        Returns:
            Any: Still in progress.
        """
        weight_class, title_bout = self._extract_weight()
        outcome = self._extract_bout_outcome()

        return weight_class, title_bout, outcome

    def _get_fight_stats_header(self) -> List[str]:
        """
        Extracts the names associated with each stat in the fight stats table.

        Returns:
            List[str]: List of prefixed stat names. (red/blue corner prefix)
        """
        header: List[str] = []
        for link in self.fight.find(class_="b-fight-details__table-head"):  # type: ignore
            # Cleans the header such that it splits entries if there has been one new line followed by 3 or more non-word characters.
            text: List[str] = re.split(r"\n\W{3,}", link.text)  # type: ignore
            filtered_text: List[str] = [
                self._clean_text(entry)
                for entry in text
                if len(self._clean_text(entry)) > 0
                for _ in range(2)
            ]
            header.extend(filtered_text)

        return self._apply_rb_prefix(header)

    def get_fight_stats(self) -> Dict[str, str]:
        """
        Extracts the stats for both fighters in the bout.

        Returns:
            Dict[str, str]: Dictionary where key = stat name and value = stat.
        """
        table: List[str] = []
        # Goes through the table containing the key information from each fight and stores the stats in a list.
        for link in self.fight.find_all(class_="b-fight-details__table-text", limit=20):
            entry: str = self._clean_text(link.get_text())
            table.append(entry)

        header: List[str] = self._get_fight_stats_header()
        header_and_table: Dict[str, str] = dict(zip(header, table))
        return header_and_table

    def get_fighter_links(self) -> List[str]:
        fighter_links: List[str] = []
        # Gets the links to each fighter's profile page and stores them in a list.
        for link in self.fight.find_all(
            "a", class_="b-link b-link_style_black", limit=2
        ):
            fighter_links.append(link.get("href"))
        return fighter_links

    def scrape_url(self):
        ...
