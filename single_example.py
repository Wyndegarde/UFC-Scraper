import json
import requests
from bs4 import BeautifulSoup

fight_tag = 'b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click'

with open("artefacts/raw_events.json") as json_file:
    raw_links = json.load(json_file)

event = raw_links['UFC 278: Usman vs. Edwards']

get = requests.get(event, timeout = 20)
soup = BeautifulSoup(get.content, 'lxml')

fight_links = [tag.get('data-link') for tag in soup.find_all('tr',class_ = fight_tag)]

one_fight = fight_links[0]
get = requests.get(one_fight, timeout = 20)
soup = BeautifulSoup(get.content, 'lxml')

print(soup)