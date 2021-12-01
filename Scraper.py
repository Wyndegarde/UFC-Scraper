import requests 
from bs4 import BeautifulSoup

import pandas as pd
from Functions import *

'''
Notes: 
22+ pages of events on website. Last page excluded due to errors in data. Might be worth coding in a fix. 

Runtime of this block: for 10 pages - 55 mins(ish), for 21 pages - 1hr 51mins. Can this be reduced? 
Effectively scraping through 5500+ fights so marginal gains on one fight would help

'''

fight_tag = 'b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click'
fighter_tag = 'b-link b-link_style_black'
weight_title_tag = 'b-fight-details__fight-title'
outcome_tag = 'b-fight-details__person'
winloss_tag = 'b-fight-details__person-status b-fight-details__person-status_style_gray'
fight_details_tag = 'b-fight-details__table-text'

all_links = [] # List to store all URLs 
ufc_URL = 'http://ufcstats.com/statistics/events/completed' # Link to UFC stats page with all events 
sequence = range(1,22)
                             # Idea: read in the page, find the section with page numbers, save 1 and then the final page text, save each as variable and use those for range. 

for i in sequence: 
  url = requests.get(ufc_URL, params={'page':i}, timeout = 10) # Gets the page, 1 through 22.
  soup = BeautifulSoup(url.content, 'lxml') # Parses the webpage 

  for link in soup.find_all('a',class_="b-link b-link_style_black", href = True): # For each link in each page, go through them
    event = link['href'] 
    all_links.append(event) 

    # print(f'added {link.text}') # Used to show which events have been added to the list. 

    
  print(f'Page {i} complete') # Just used as indicator to show page has been processed. 

# Notes: Gathered the names through scraping, then added red/blue prefixes.
 
fight_column_names =['date','location', 'red_fighter', 'blue_fighter', 'winner', 'weight_class','title_fight',
'red_knockdowns','blue_knockdowns', 'red_sig_strike', 'blue_sig_strike', 'red_sig_strike_percent', 'blue_sig_strike_percent', 
'red_total_strikes', 'blue_total_strikes', 'red_takedowns', 'blue_takedowns', 'red_takedown_percent', 'blue_takedown_percent',
'red_submission_attempts', 'blue_submission_attempts', 'red_reversals', 'blue_reversals', 'red_control_time', 'blue_control_time']

fighter_info_columns = ['red_Record','red_Height','red_Weight','red_Reach','red_STANCE','red_DOB','red_SLpM',
'red_Str_Acc','red_SApM','red_Str_Def','red_TD_Avg','red_TD_Acc','red_TD_Def','red_Sub_Avg',
'blue_Record','blue_Height','blue_Weight','blue_Reach','blue_STANCE','blue_DOB','blue_SLpM',
'blue_Str_Acc','blue_SApM','blue_Str_Def','blue_TD_Avg','blue_TD_Acc','blue_TD_Def','blue_Sub_Avg']

event_stats = pd.DataFrame(columns = fight_column_names)
fighter_profile_df = pd.DataFrame(columns = fighter_info_columns)

for event in all_links:           # Goes through each event that was saved. 
  ufc_card = parse_webpage(event) # Parses each event. 


  event_info = ufc_card.find(class_ = 'b-list__box-list').text.replace('\n','').split('      ') # Gets the Date and Location. 
  date = event_info[3]
  location = event_info[-1]
  fight_links = [tag.get('data-link') for tag in ufc_card.find_all('tr',class_ = fight_tag)]

  for fights in fight_links: # Goes the statistics page of each fight for each event. 
    red_vs_blue = parse_webpage(fights) 
    fighter_links = [link.get('href') for link in red_vs_blue.find_all('a',class_ = fighter_tag, limit = 2)]

    weight = red_vs_blue.find(class_ = weight_title_tag).text
    if 'Title' in weight: 
      title_bout = 'Y'
    else:
      title_bout = 'N'
    weightclass = strip_ufc_text(weight).replace(' Bout','').replace(' Title','')  

    all_info = []
    for link in fighter_links: # We get the links for both fighters in each fight and go through both. 
      profile = parse_webpage(link)
      record = profile.find(class_ = 'b-content__title-record')
      all_info.append(strip_ufc_text(record.text).split(':'))   # Strip it down and add it to the list

      career_info = profile.find_all(class_="b-list__box-list-item b-list__box-list-item_type_block") # Next we go through all of the summary stats for each fighter. 
      for each in career_info:
        output = strip_ufc_text(each.text).split(':') # Info has "category:value" format. So use split to seperate them
        all_info.append(output) # Add the info for each fighter to the list. This adds all red fighter stats, then loops through again to add blue fighter stats to end of that. 

    all_info.remove(all_info[10]) # This is an empty entry due to website formatting. 
    all_info.remove(all_info[-5]) # see above 
    all_fighter_stats = [i[1] for i in all_info] 

    afs_series = pd.Series(all_fighter_stats, index = fighter_profile_df.columns) # converts this list to a series so it can be added to the dataframe. 
    fighter_profile_df = fighter_profile_df.append(afs_series, ignore_index=True) # Finally add the fighter stats to the dataframe. 
    
    outcome = red_vs_blue.find(class_ = outcome_tag).find(class_ = winloss_tag)
    if outcome == None:
      win = 'W'
    else: 
      win= strip_ufc_text(outcome.text)
    
    table = [strip_ufc_text(link.get_text()) for link in red_vs_blue.find_all(class_ = fight_details_tag, limit = 20)] # only first 20 entries relevant

    # This code here adds the date, location and winner information to the list and then adds that row to the master dataframe. 
    table.insert(0,date)
    table.insert(1,location)
    table.insert(4,win)
    table.insert(5,weightclass)
    table.insert(6,title_bout)
    stats = pd.Series(table, index = fight_column_names)
    event_stats = event_stats.append(stats,ignore_index=True)

UFC_DataFrame = pd.concat([event_stats,fighter_profile_df],axis = 1)
UFC_DataFrame.to_csv('ufc_raw.csv',index = False)