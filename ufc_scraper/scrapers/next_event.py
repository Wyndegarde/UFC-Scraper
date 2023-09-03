
from ufc_scraper.base_classes import ScraperABC

class NextEventScaper(ScraperABC):
    def __init__(self, url: str) -> None:
        super().__init__(url)

    def get_next_event(self):
        next_event = self._get_soup()

        fight_links = []
        for tag in next_event.find_all():
            link_to_fight = tag.get('data-link')
            if link_to_fight:
                fight_links.append(link_to_fight)
        
        fight_links = list(dict.fromkeys(fight_links))
        del fight_links[0]

        # date_location = next_event.find(class_ = 'b-list__box-list').text.replace('\n','').split('    ')
        # date = date_location[5]
        # location = date_location[-2]

        for link in fight_links:
            # Use fighter 
            fight = 2
            print(fight)
