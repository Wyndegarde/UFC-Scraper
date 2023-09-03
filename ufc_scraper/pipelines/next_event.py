from typing import List, Dict
from ufc_scraper.config import PathSettings
from ufc_scraper.scrapers import (
    HomepageScraper,
    BoutScraper,
    FighterScraper,
    CardScraper,
)

class NextEventPipeline:
    def _scrape_fighter_profiles(self, fighter_links: List[str]) -> Dict[str, str]:
        """
        Method responsible for extracting the fighter profiles from the bout and formating them.

        Args:
            fighter_links (List[str]): URLS to all found fighter profiles

        Returns:
            Dict[str, str]: All extracted info as a dictionary. keys prefixed by corner of each fighter.
        """

        assert len(fighter_links) >= 2, "There should be two fighters per bout."

        # Create object to extract info for each corner.
        red_fighter = FighterScraper(fighter_links[0], red_corner=True)
        blue_fighter = FighterScraper(fighter_links[1], red_corner=False)

        # Scrape the info for each fighter.
        red_fighter_profile: Dict[str, str] = red_fighter.scrape_url()
        blue_fighter_profile: Dict[str, str] = blue_fighter.scrape_url()

        # Combine the two dictionaries into one.
        fighter_profiles: Dict[str, str] = {
            **red_fighter_profile,
            **blue_fighter_profile,
        }

        return fighter_profiles
    def scrape_next_event(self):
        homepage = HomepageScraper(
            url="http://www.ufcstats.com/statistics/events/completed",
            cache_file_path=PathSettings.EVENT_CACHE_JSON,
        )
        next_event_link = homepage._get_next_event()

        fight_card = CardScraper(next_event_link)
        event_name, date, location, fight_links = fight_card.scrape_url()
        fight_links = list(set(fight_links))
        all_fights = []
        for fight in fight_links:
            bout = BoutScraper(url=fight, date=date, location=location)
            fighter_links = bout.get_fighter_links()
            fighter_profiles = self._scrape_fighter_profiles(fighter_links)
            
            all_info = bout.extract_future_bout_stats()

            combined_info = {**all_info, **fighter_profiles}

            all_fights.append(combined_info)
        return all_fights