import pandas as pd
import numpy as np
from Functions import *

from datetime import datetime
import statsmodels.formula.api as smf
from sklearn.preprocessing import LabelEncoder

UFC_DataFrame = pd.read_csv('ufc_raw.csv')

# Find out how to do this in Regex. 
words = ['\d+',' Tournament','Interim ','UFC ','Australia ','UK ','vs. ','Brazil ', 'China ','TUF Nations Canada ','America ', 'Latin ','Ultimate Fighter  ','Ultimate Fighter ']
for word in words:
  UFC_DataFrame['weight_class'] = UFC_DataFrame['weight_class'].str.replace(word,'')

drop_columns = []
for column in UFC_DataFrame.columns:
  if len(UFC_DataFrame[column][UFC_DataFrame[column] == '---']) > 0:
    drop_columns.append(column)
    #print(column, len(UFC_DataFrame[column][UFC_DataFrame[column] == '---']))

height_reach = []
for column in UFC_DataFrame.columns:
  if 'Reach' in column or 'Height' in column:
    height_reach.append(column)

UFC = UFC_DataFrame.copy()

grouped_df = UFC.copy()
grouped_df = grouped_df.dropna(subset = height_reach)

for column in height_reach:
  if 'Height' in column:
    grouped_df[column] = grouped_df[column].apply(lambda x:height_to_cm(x))
  else:
    grouped_df[column] = grouped_df[column].apply(lambda x:reach_cm(x))

grouping_by_weight_classes = grouped_df.groupby('weight_class').mean()
reach_height_df = grouping_by_weight_classes[height_reach]

UFC = UFC[UFC['blue_DOB'] != '--']
UFC = UFC[UFC['red_DOB'] != '--']
UFC = UFC.drop(drop_columns,axis = 1)

UFC['date'] = UFC['date'].apply(lambda x: datetime.strptime(x,'%B %d, %Y')) 

for column in UFC.columns: 
  if 'DOB' in column:
    UFC[column] = UFC[column].apply(lambda x: datetime.strptime(x,'%b %d, %Y')) 

UFC = UFC.replace('---','0')
UFC['blue_STANCE'] = UFC['blue_STANCE'].replace(np.nan,'Orthodox') # Choosing the replace with Orthodox because it is the most common stance. 
UFC['red_STANCE'] = UFC['blue_STANCE'].replace(np.nan,'Orthodox') # see above
#UFC = UFC.sort_values(by = 'date', ascending = False) # This is not totally necessary, but handy for if anything gets jumbled up later on when appending. 

UFC_subset = UFC.copy()
UFC_subset = UFC_subset[['date', 'location', 'red_fighter', 'blue_fighter', 'winner','weight_class','title_fight','red_sig_strike','blue_sig_strike', 
                                 'red_total_strikes', 'blue_total_strikes', 'red_takedowns','blue_takedowns',
                                 'red_submission_attempts', 'blue_submission_attempts', 'red_Record',
                                 'red_Height', 'red_Weight', 'red_Reach', 'red_STANCE', 'red_DOB', 'blue_Record', 'blue_Height',
                                 'blue_Weight', 'blue_Reach', 'blue_STANCE', 'blue_DOB']]


# This block here pulls all the percentage columns, then removes the % from each and converts them to decimal. 
percent_names = []
of_columns = []
height_columns = []
reach_columns = []

for name in UFC_subset.columns: 

  if 'percent' in name:
    percent_names.append(name)

  elif UFC_subset[name].dtype == object and sum(UFC_subset[name].apply(lambda x: 'of' in str(x))) > 0 and name != 'red_fighter' and name != 'blue_fighter' : # This is definitely not the best way to do this, find better way.
    of_columns.append(name) # This block gets all the columns with ' x of y' in them and stores them in a list for processing.

  elif 'Height' in name: # This block converts the height and reach columns from inches to cm. 
    height_columns.append(name)
    UFC_subset[name] = UFC_subset[name].apply(lambda x:height_to_cm(x))

  elif 'Reach' in name: 
    reach_columns.append(name)
    UFC_subset[name] = UFC_subset[name].apply(lambda x:reach_cm(x))


for column in percent_names: 
  UFC_subset[column] = UFC_subset[column].str.strip('%').astype('int')/100


for column in of_columns: # This block converts all the columns from strings containing "x of y" to two columns corresponding to attempted and landed. 
  column_as_list = UFC_subset[column].tolist()
  splitting_column = []

  for each in column_as_list: 
    splitting_column.append(each.split(' of '))
  
  attempted = [float(i[1]) for i in splitting_column] 
  landed = [float(i[0]) for i in splitting_column] 

  attempted_suffix = column + '_attempted'
  landed_suffix = column + '_landed'
  percent_suffix = column + '_percent'
 
  UFC_subset[attempted_suffix] = attempted 
  UFC_subset[landed_suffix] = landed
  UFC_subset[percent_suffix] =  UFC_subset[landed_suffix] / UFC_subset[attempted_suffix] 
  UFC_subset[percent_suffix] = UFC_subset[percent_suffix].fillna(0)

  UFC_subset = UFC_subset.drop(columns = column)

missing_value_df = UFC_subset.copy()
missing_value_df = missing_value_df[missing_value_df.isna().any(axis = 1)] # Could make more generic and have the loop below run through all of UFC subset, but wanted to cut run time down. 
missing_value_df = missing_value_df[height_reach]

for column in height_reach:
  for i in missing_value_df.index:
    if np.isnan(missing_value_df.loc[i,column]) == True:
      UFC_subset.loc[i,column] = reach_height_df.loc[UFC_subset.loc[i,'weight_class'],column]

UFC_subset['Height_diff'] = UFC_subset[height_columns[0]] - UFC_subset[height_columns[1]] # Red height minus Blue height. So positve value suggests red taller, negative implies red shorter.
UFC_subset['Reach_diff'] = UFC_subset[reach_columns[0]] - UFC_subset[reach_columns[1]]  # Same as for height. 

UFC_subset['red_age'] = UFC_subset['date'].sub(UFC_subset['red_DOB']).dt.days.div(365.25).round(0).astype(int)
UFC_subset['blue_age'] = UFC_subset['date'].sub(UFC_subset['blue_DOB']).dt.days.div(365.25).round(0).astype(int)

# I need: strike defence and takedown defence for red and blue fighters
 
UFC_subset['red_sig_strike_defence_percent'] = 1-  UFC_subset['blue_sig_strike_percent'] 
UFC_subset['blue_sig_strike_defence_percent'] = 1-  UFC_subset['red_sig_strike_percent'] 

UFC_subset['red_takedowns_defence_percent'] = 1-  UFC_subset['blue_takedowns_percent'] 
UFC_subset['blue_takedowns_defence_percent'] = 1-  UFC_subset['red_takedowns_percent'] 

number_of_fights_per_fighter = UFC_subset['red_fighter'].append(UFC_subset['blue_fighter']).value_counts()

UFC_key_columns = UFC_subset.copy()
UFC_key_columns = UFC_key_columns[['date','red_fighter','blue_fighter','winner',
                                   'red_sig_strike_percent', 'blue_sig_strike_percent',
                                   'red_submission_attempts', 'blue_submission_attempts', 
                                   'red_STANCE', 'blue_STANCE', 'red_total_strikes_percent',
                                   'blue_total_strikes_percent', 'red_takedowns_percent',
                                   'blue_takedowns_percent', 'Height_diff', 'Reach_diff', 
                                   'red_age','blue_age','red_sig_strike_defence_percent',
                                   'blue_sig_strike_defence_percent', 'red_takedowns_defence_percent',
                                   'blue_takedowns_defence_percent']]

fighters = np.unique(np.concatenate([UFC_subset['red_fighter'], UFC_subset['blue_fighter'] ], axis = None)) 

percent_stats = []
for column in UFC_subset.columns:
  if 'percent' in column and not 'total' in column:
    column_name = column.replace('red_','').replace('blue_','')
    if column_name not in percent_stats:
      percent_stats.append(column_name)
      #print(column_name)

# Runtime of block: 1 minute, 30 seconds  - Suggests I may need to improve the loops/algorithm
regression_df = pd.DataFrame()

# Aim for this block of code is to go through each fighter, get the averages they had going into fight t and fight t-1 
# use these to build our X & Y's for the linear regression. Then do this for each relevant stat. 
# Lets us build a linear regression with 3000+ rows of data but have them relevant to each fighter. 

for column in percent_stats:       
  each_stat_df = pd.DataFrame(columns = [column, 'Y_' + column, 'X_' + column]) # Creates a dataframe for each stat. 

  for fighter in fighters: 
    fighter_df = get_fighter(UFC_key_columns,fighter).sort_values(by = 'date', ascending = True) # Gets each fighter and orders their fights, earliest to most recent.

    if len(fighter_df) >= 3: # The dataframe will only work if fighter has 3 or more fights. 
      ordered_stats = []

      for i in fighter_df.index:                      # stores the stat from every fight in a list, accounting for the fact they may be in a different corner (red/blue) each fight
        if fighter in fighter_df.loc[i,'red_fighter']:
          ordered_stats.append(fighter_df.loc[i,'red_' + column])
        if fighter in fighter_df.loc[i,'blue_fighter']:
          ordered_stats.append(fighter_df.loc[i,'blue_' + column])

      lin_reg_df =  pd.DataFrame(ordered_stats, columns=[column])                # Goes through and builds the X and Y data for the linear regression model. 
      lin_reg_df['X_' + column] = lin_reg_df[column].expanding(2).mean().shift(1)
      lin_reg_df.loc[1,'X_' + column] = lin_reg_df.loc[0,column]
      lin_reg_df['Y_' + column] = lin_reg_df['X_' + column].shift(1)
      lin_reg_df = lin_reg_df.dropna()

      each_stat_df = pd.concat([each_stat_df,lin_reg_df], axis = 0) # Adds the rows of each fighter to the dataframe for that stat. 

  regression_df = pd.concat([regression_df,each_stat_df], axis = 1) # Adds the columns for each stat to the master DF. 

regression_df = regression_df.reset_index(drop = True) # Just resets the index. 

XYs_only = regression_df.drop(percent_stats, axis = 1)

sig_strike_model = smf.ols('Y_sig_strike_percent	~ X_sig_strike_percent', data = XYs_only).fit()
takedowns_model = smf.ols('Y_takedowns_percent	~ X_takedowns_percent', data = XYs_only).fit()


sig_strike_defence_model = smf.ols('Y_sig_strike_defence_percent	~ X_sig_strike_defence_percent', data = XYs_only).fit()
takedowns_defence_model = smf.ols('Y_takedowns_defence_percent	~ X_takedowns_defence_percent', data = XYs_only).fit()

sig_strike_pred_val = sig_strike_model.fittedvalues.copy()
sig_strike_true_val = XYs_only['Y_sig_strike_percent'].values.copy()
sig_strike_residual = sig_strike_true_val - sig_strike_pred_val

takedowns_pred_val = takedowns_model.fittedvalues.copy()
takedowns_true_val = XYs_only['Y_takedowns_percent'].values.copy()
takedowns_residual = takedowns_true_val - takedowns_pred_val

sig_strike_defence_pred_val = sig_strike_defence_model.fittedvalues.copy()
sig_strike_defence_true_val = XYs_only['Y_sig_strike_defence_percent'].values.copy()
sig_strike_defence_residual = sig_strike_defence_true_val - sig_strike_defence_pred_val

takedowns_defence_pred_val = takedowns_defence_model.fittedvalues.copy()
takedowns_defence_true_val = XYs_only['Y_takedowns_defence_percent'].values.copy()
takedowns_defence_residual = takedowns_defence_true_val - takedowns_defence_pred_val

red_blue_percent_stats = []
for column in UFC_subset.columns:
  if 'percent' in column and 'total' not in column:
    red_blue_percent_stats.append(column)

new_columns = []
for name in red_blue_percent_stats:
  string = name.replace('percent','average')
  new_columns.append(string)
  UFC_subset[string] = np.nan

for fighter in fighters:
  fighter_df = get_fighter(UFC_subset,fighter).sort_values(by = 'date', ascending = True) # Gets each fighter and orders their fights, earliest to most recent.

  if len(fighter_df) > 1: 
    sig_strikes = []
    takedowns = []
    sig_strike_defence = []
    takedown_defence = []

    for i in fighter_df.index:

      if fighter in fighter_df.loc[i,'red_fighter']:
        sig_strikes.append(fighter_df.loc[i,'red_sig_strike_percent'])
        takedowns.append(fighter_df.loc[i,'red_takedowns_percent'])
        sig_strike_defence.append(fighter_df.loc[i,'red_sig_strike_defence_percent'])
        takedown_defence.append(fighter_df.loc[i,'red_takedowns_defence_percent'])

      if fighter in fighter_df.loc[i,'blue_fighter']:
        sig_strikes.append(fighter_df.loc[i,'blue_sig_strike_percent'])
        takedowns.append(fighter_df.loc[i,'blue_takedowns_percent'])
        sig_strike_defence.append(fighter_df.loc[i,'blue_sig_strike_defence_percent'])
        takedown_defence.append(fighter_df.loc[i,'blue_takedowns_defence_percent'])

    dic = {'sig_strike':sig_strikes,'takedowns':takedowns,'sig_strike_defence':sig_strike_defence,'takedowns_defence':takedown_defence}
    df = pd.DataFrame(dic,index = fighter_df.index)
    
    for column in df.columns:
      column_name = column + '_average'
      df[column_name] =df[column].expanding(2).mean().shift(1)
      df.loc[df.index[1],column_name] = df.loc[df.index[0],column]
    
    predict_sig_strikes = sig_strike_model.predict(exog = dict(X_sig_strike_percent=df.loc[df.index[1],'sig_strike_average']))
    predict_takedowns = takedowns_model.predict(exog = dict(X_takedowns_percent=df.loc[df.index[1],'takedowns_average']))

    predict_sig_strike_defence = sig_strike_defence_model.predict(exog = dict(X_sig_strike_defence_percent=df.loc[df.index[1],'sig_strike_defence_average']))
    predict_takedown_defence = takedowns_defence_model.predict(exog = dict(X_takedowns_defence_percent=df.loc[df.index[1],'takedowns_defence_average']))

    df.loc[df.index[0],'sig_strike_average'] = predict_sig_strikes[0]
    df.loc[df.index[0],'takedowns_average'] = predict_takedowns[0]
    df.loc[df.index[0],'sig_strike_defence_average'] = predict_sig_strike_defence[0]
    df.loc[df.index[0],'takedowns_defence_average'] = predict_takedown_defence[0]

    df = df.drop(columns = ['sig_strike', 'takedowns', 'sig_strike_defence', 'takedowns_defence'])

    for column in df.columns: 
      for i in df.index:
        if fighter in UFC_subset.loc[i,'red_fighter']:
          UFC_subset.loc[i,'red_' + column] = df.loc[i,column]
        elif fighter in UFC_subset.loc[i,'blue_fighter']:
          UFC_subset.loc[i,'blue_' + column] = df.loc[i,column]

UFC_drop_nas = UFC_subset.dropna()

UFC_drop_nas.to_csv('UFC_cleaned.csv',index = False)