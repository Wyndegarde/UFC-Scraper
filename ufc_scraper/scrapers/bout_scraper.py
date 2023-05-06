from ufc_scraper.base_classes import ScraperABC

class BoutScraper(ScraperABC):

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.fight = self._get_soup()

    def _extract_weight(self):
        weight = self.fight.find(class_ = 'b-fight-details__fight-title').text

        if 'Title' in weight: 
            title_bout = 'Y'
        else:
            title_bout = 'N'

        cleaned_weight_class = self._clean_text(weight).replace(' Bout','').replace(' Title','')  

        return cleaned_weight_class, title_bout
    
    def _extract_bout_outcome(self):
        outcome = self.fight.find(class_ = 'b-fight-details__person').find(class_ = 'b-fight-details__person-status b-fight-details__person-status_style_gray')
        if outcome:
            win = self._clean_text(outcome.text)
        else:
            win = "W"
        return win
    
    def _get_fight_details(self):
        weight_class, title_bout = self._extract_weight()
        outcome = self._extract_bout_outcome()
        
    def _get_fight_stats(self):
        ...

    def _get_fighter_links(self):
        fighter_links = []
        for link in self.find_all('a',class_ = 'b-link b-link_style_black',limit = 2): # Gets the links to each fighter's profile page and stores them in a list. 
            fighter_links.append(link.get('href'))
        return fighter_links

        
    def scrape_url(self):
        ...