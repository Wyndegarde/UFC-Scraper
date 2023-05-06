from ufc_scraper.base_classes import ScraperABC

class FighterScraper(ScraperABC):
    def __init__(self, url):
        super().__init__(url)
        self.fighter = self._get_soup()

    def _get_figther_details(self):
              
      record = self.fighter.find(class_ = 'b-content__title-record') # First find their record. 
      cleaned_record = self._clean_text(record.text).split(':')  # Strip it down and add it to the list

      career_info = self.fighter.find_all(class_="b-list__box-list-item b-list__box-list-item_type_block") # Next we go through all of the summary stats for each fighter. 
      all_info = [] # Create a list to store all of the info for each fighter.
      
      for each in career_info:
        output = self._clean_text(each.text).split(':') # Strip the text containing the info and then split it by colons, to have a list where each entry is a 2 element list containing the name of the stat and the stat itself. 
        all_info.append(output) # Add the info for each fighter to the list. This adds all red fighter stats, then loops through again to add blue fighter stats to end of that. 
