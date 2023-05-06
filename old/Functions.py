import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def parse_webpage(link):
  get = requests.get(link, timeout = 20)
  soup = BeautifulSoup(get.content, 'lxml')
  return(soup)
  
def strip_ufc_text(text):
  text = text.strip().replace('\n','').replace("    ",'')
  return(text)

def get_fighter(df,fighter): 
  df1 = df[df['red_fighter'] == fighter ] 
  df2 = df[df['blue_fighter'] == fighter ]
  df3 = pd.concat([df1,df2],axis = 0)
  return(df3)

# Taken from Lewis' code

#Function for changing height column to inches and then to cm 
def height_to_cm(height):
  if height == '--': 
    return(np.nan)
  else:
    height =height.split("' ")
    feet = float(height[0])
    inch = float(height[1].replace("\"",""))
    feet_inch = (12*feet) + inch
    return(feet_inch*2.54)


#Convert both reach columns into cm
def reach_cm(reach):
    if reach == '--': # bit of a messy change, but currently I replace all of these strings with NaN, then work out the newly mean of the column excluding these values and finally replace the NaN with the mean. 
        return(np.nan)
    else: 
        reach = float(reach.replace('"',''))
        return(reach*2.54) 