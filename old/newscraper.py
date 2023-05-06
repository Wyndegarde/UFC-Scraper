import os
from loguru import logger
import requests 
import json
from bs4 import BeautifulSoup
import pandas as pd


#from config.Functions import *
from config import Config as config


'''
Go through page, create dictionary. key = name of event. value = link. output to JSON
have one JSON for processed fights, one for unprocessed. only scrape links within unprocessed JSON. 
'''

logger.add(config.scraper_log, format = config.format, 
           rotation= config.rotation, enqueue=True)

raw_links = {}
processed_links = {}
ufc_URL = 'http://ufcstats.com/statistics/events/completed' # Link to UFC stats page with all events 
sequence = range(1,22)

for i in sequence: 
  url = requests.get(ufc_URL, params={'page':i}, timeout = 10) # Gets the page, 1 through 22.
  soup = BeautifulSoup(url.content, 'lxml') # Parses the webpage 

  for link in soup.find_all('a',class_="b-link b-link_style_black", href = True): # For each link in each page, go through them

    event_link = link['href'] 
    event_name = link.contents[0].strip()
    raw_links[event_name] = event_link

with open("artefacts/raw_events.json", "w") as w:
    json.dump(raw_links, w, indent = 2)















class Scraper:

  def __init__(self):
    self.ufc_urls = 'http://ufcstats.com/statistics/events/completed'

  def get_fight_links(self):
    for i in sequence: 
      url = requests.get(ufc_URL, params={'page':i}, timeout = 10) # Gets the page, 1 through 22.
      soup = BeautifulSoup(url.content, 'lxml') # Parses the webpage 

      for link in soup.find_all('a',class_="b-link b-link_style_black", href = True): # For each link in each page, go through them

        event_link = link['href'] 
        event_name = link.contents[0].strip()
        raw_links[event_name] = event_link

    with open("artefacts/raw_events.json", "w") as w:
        json.dump(raw_links, w, indent = 2)

    return
