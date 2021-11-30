import pandas as pd
from Functions import *

from datetime import datetime, date

cleaned_ufc = pd.read_csv('UFC_cleaned.csv')

# Got these column names through scraping a single fight then manually editing them to match the historical data. 
# May be a better way to do this to avoid explicitly creating the dataframe before scraping. 

event_df = pd.DataFrame(columns = ['date', 'location', 'red_fighter', 'blue_fighter', 'weight_class',
       'title_fight', 'red_Record', 'red_Average Fight Time', 'red_Height',
       'red_Weight', 'red_Reach', 'red_STANCE', 'red_DOB',
       'red_Strikes Landed per Min.', 'red_sig_strike_average',
       'red_Strikes Absorbed per Min. (SApM)', 'red_sig_strike_defence_average',
       'red_Takedowns Average/15 min.', 'red_takedowns_average',
       'red_takedowns_defence_average', 'red_Submission Average/15 min.', 'blue_Record',
       'blue_Average Fight Time', 'blue_Height', 'blue_Weight', 'blue_Reach',
       'blue_STANCE', 'blue_DOB', 'blue_Strikes Landed per Min. (SLpM)',
       'blue_sig_strike_average', 'blue_Strikes Absorbed per Min. (SApM)',
       'blue_sig_strike_defence_average', 'blue_Takedowns Average/15 min.',
       'blue_takedowns_average', 'blue_takedowns_defence_average',
       'blue_Submission Average/15 min.'])

webpage = parse_webpage('http://ufcstats.com/statistics/events/completed')
next_event_link = webpage.find(class_ = 'b-link b-link_style_white')['href'] # It seems style_white is for future events, and style_black is for past events. Check this later
next_event = parse_webpage(next_event_link)

fight_links = []
for tag in next_event.find_all():
  link_to_fight = tag.get('data-link')
  if link_to_fight != None:
    fight_links.append(link_to_fight)

fight_links = list(dict.fromkeys(fight_links))
del fight_links[0]

date_location = next_event.find(class_ = 'b-list__box-list').text.replace('\n','').split('    ')
date = date_location[5]
location = date_location[-2]

for link in fight_links: 
  fight = parse_webpage(link)

  info = []
  for entry in fight.find_all(class_ = 'b-fight-details__table-text'):
    info.append(strip_ufc_text(entry.text))

  less_info = info[0:45] # The number of entries we want. 
  del less_info[::3]

  red_fighter = less_info[::2]
  del less_info[::2]

  blue_fighter = less_info

  all_stats = red_fighter + blue_fighter

  names = []
  for name in fight.find_all(class_='b-fight-details__table-header-link'):
    names.append(strip_ufc_text(name.text)) 

  words = ['\d+',' Title',' Bout',' Tournament','Interim ','UFC ','Australia ','UK ','vs. ','Brazil ', 
          'China ','TUF Nations Canada ','America ', 'Latin ','Ultimate Fighter  ','Ultimate Fighter ']
  weight = strip_ufc_text(fight.find(class_ = 'b-fight-details__fight-title').text)

  if 'Title' in weight: 
    title_bout = 'Y'
  else:
    title_bout = 'N'

  for word in words:
    weight = weight.replace(word,'')

  additional_info = [date] + [location] + names  + [weight] + [title_bout]

  all_stats = additional_info + all_stats

  event_df.loc[len(event_df)] = all_stats

for column in event_df:
  if 'Height' in column:
    event_df[column] = event_df[column].apply(lambda x:height_to_cm(x))
  elif 'Reach' in column:
    event_df[column] = event_df[column].apply(lambda x:reach_cm(x))
  elif 'DOB' in column:
    event_df[column] = event_df[column].apply(lambda x: datetime.strptime(x,'%b %d, %Y')) 
  elif 'average' in column:
    event_df[column] = event_df[column].apply(lambda x: int(x.strip('%'))/100)

event_df['date'] = event_df['date'].apply(lambda x: datetime.strptime(x,'%B %d, %Y')) 

event_df['Height_diff'] = event_df['red_Height'] - event_df['blue_Height'] 
event_df['Reach_diff'] = event_df['red_Reach'] - event_df['blue_Reach'] 

event_df['red_age'] = event_df['date'].sub(event_df['red_DOB']).dt.days.div(365.25).round(0).astype(int)
event_df['blue_age'] = event_df['date'].sub(event_df['blue_DOB']).dt.days.div(365.25).round(0).astype(int)


Next_event = event_df.to_csv('Next_Event.csv', index = False)
