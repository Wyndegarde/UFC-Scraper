from typing import Dict, Any
import pandas as pd

from ufc_scraper.data_processing import RawDataProcessor, CacheProcessor
from ufc_scraper.scrapers import (
    HomepageScraper,
    BoutScraper,
    FighterScraper,
    CardScraper,
)


class ScrapingPipeline:
    """
    Runs the pipeline to scrape the UFC stats data

    #! NOTE: This is just a copilot suggestion for now - need to refine.
    #! Added so there was a starting point.
    """

    def run_pipeline(self) -> Any:
        homepage = HomepageScraper(
            "http://www.ufcstats.com/statistics/events/completed"
        )
        links = homepage.scrape_url()

        for link in links:
            fight_card = CardScraper(link)
            date, location = fight_card.get_event_details()
            fight_links = fight_card.get_fight_links()

            for fight in fight_links:
                bout = BoutScraper(url=fight, date=date, location=location)
                full_bout_details, fighter_links = bout.scrape_url()

                assert len(fighter_links) >= 2, "There should be two fighters per bout."

                red_fighter = FighterScraper(fighter_links[0], red_corner=True)
                blue_fighter = FighterScraper(fighter_links[1],red_corner=False)

                red_fighter_profile:  Dict[str, str] = red_fighter.scrape_url()
                blue_fighter_profile:  Dict[str, str] = blue_fighter.scrape_url()

                fighter_profiles: Dict[str, str] = {**red_fighter_profile, **blue_fighter_profile}

                full_fight_details = {**full_bout_details,**fighter_profiles}

                full_fight_details_df =  pd.DataFrame.from_dict(
                    full_fight_details, orient="index"
                ).T