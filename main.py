import pandas as pd

from ufc_scraper.scrapers import (
    HomepageScraper,
    BoutScraper,
    FighterScraper,
    CardScraper,
)


def test_single_event():
    output_dataframe = pd.DataFrame()
    # Scrape latest event. Get info and fight links
    test_card = CardScraper("http://www.ufcstats.com/event-details/3c6976f8182d9527")
    date, location = test_card.get_event_details()
    fight_links = test_card.get_fight_links()
    print(date, location)
    # Scrape a signle fight from the event
    first_fight = BoutScraper(fight_links[0])

    bout_stats = first_fight._extract_bout_stats()
    print(bout_stats)

    # add bout stats to df
    bout_stats_df = pd.DataFrame.from_dict(bout_stats, orient="index").T
    output_dataframe = pd.concat([output_dataframe, bout_stats_df], axis=0)

    fighter_profile_links = first_fight.get_fighter_links()

    for fighter_profile_url in fighter_profile_links:
        # Scrape a single fighter profile
        fighter_profile = FighterScraper(fighter_profile_url)
        fighter_stats = fighter_profile.get_fighter_details()
        print(fighter_stats)

    # output dataframe to csv
    output_dataframe.to_csv("test.csv", index=False)


test_single_event()


def test_homepage():
    homepage_scraper = HomepageScraper(
        "http://www.ufcstats.com/statistics/events/completed"
    )
    links = homepage_scraper.scrape_url()
    print(links)


# def bout_test():
#     bout_scraper = BoutScraper("http://www.ufcstats.com/fight-details/2b1ac5d8f98639bf")

#     weight, title = bout_scraper._extract_weight()

#     fighter_links = bout_scraper._get_fighter_links()
#     # print(fighter_links)

#     # print(bout_scraper._get_fight_stats())
#     header, table = bout_scraper._get_fight_stats()

#     print(len(header))
#     print(len(table))

#     combined = dict(zip(header, table))
#     print(combined)


# def fighter_test():
#     figher_scraper = FighterScraper(
#         "http://www.ufcstats.com/fighter-details/efb96bf3e9ada36f"
#     )
#     all_info = figher_scraper.get_figther_details()
#     print(all_info)


# fighter_test()
