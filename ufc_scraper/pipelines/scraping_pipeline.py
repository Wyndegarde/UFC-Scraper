import pandas as pd

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

    def run_pipeline(self):
        homepage = HomepageScraper(
            "http://www.ufcstats.com/statistics/events/completed"
        )
        links = homepage.scrape_url()

        for link in links:
            fight_card = CardScraper(link)
            date, location = fight_card.get_event_details()
            fight_links = fight_card.get_fight_links()

            for fight in fight_links:
                bout = BoutScraper(fight)
                bout_stats = bout.get_fight_stats()
                bout_stats_df = pd.DataFrame.from_dict(bout_stats, orient="index").T

                #! This is wrong. need to instantiate the dataframe object.
                self.output_dataframe = pd.concat(
                    [self.output_dataframe, bout_stats_df], axis=0
                )
                fighter_profile_links = bout.get_fighter_links()
                for fighter_profile_url in fighter_profile_links:
                    fighter_profile = FighterScraper(fighter_profile_url)
                    fighter_stats = fighter_profile.get_fighter_details()
                    self.output_dataframe = pd.concat(
                        [self.output_dataframe, fighter_stats], axis=0
                    )
