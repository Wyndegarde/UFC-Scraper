from ufc_scraper.scrapers import HomepageScraper, BoutScraper

bout_scraper = BoutScraper("http://www.ufcstats.com/fight-details/2b1ac5d8f98639bf")

weight, title = bout_scraper._extract_weight()

fighter_links = bout_scraper._get_fighter_links()
# print(fighter_links)

print(bout_scraper._get_fight_stats())