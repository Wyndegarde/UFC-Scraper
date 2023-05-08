from ufc_scraper.scrapers import HomepageScraper, BoutScraper, FighterScraper

def bout_test():
    bout_scraper = BoutScraper("http://www.ufcstats.com/fight-details/2b1ac5d8f98639bf")

    weight, title = bout_scraper._extract_weight()

    fighter_links = bout_scraper._get_fighter_links()
    # print(fighter_links)

    # print(bout_scraper._get_fight_stats())
    header, table = bout_scraper._get_fight_stats()

    print(len(header))
    print(len(table))

    combined = dict(zip(header,table))
    print(combined)

def fighter_test():
    figher_scraper = FighterScraper("http://www.ufcstats.com/fighter-details/efb96bf3e9ada36f")
    all_info = figher_scraper._get_figther_details()
    print(all_info)

fighter_test()