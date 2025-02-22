# Base columns that are common across different uses
BASE_COLUMNS = [
    "red_fighter",
    "blue_fighter",
    "red_stance",
    "blue_stance",
    "height_diff",
    "reach_diff",
]

# Columns used for model training and inference
STAT_COLUMNS = [
    "red_sig_strike_defence_average",
    "blue_sig_strike_defence_average",
    "red_td_defence_average",
    "blue_td_defence_average",
    "red_td_average",
    "blue_td_average",
    "red_sig_str_average",
    "blue_sig_str_average",
]

# Additional columns for raw UFC data
RAW_DATA_COLUMNS = [
    "date",
    "location",
    "weight_class",
    "title_bout",
    "winner",
    "red_sig_str_percent",
    "blue_sig_str_percent",
    "red_sub_att",
    "blue_sub_att",
    "red_total_str_percent",
    "blue_total_str_percent",
    "red_td_percent",
    "blue_td_percent",
    "red_age",
    "blue_age",
    "red_sig_strike_defence_percent",
    "blue_sig_strike_defence_percent",
    "red_td_defence_percent",
    "blue_td_defence_percent",
]

NEXT_EVENT_KEY_COLUMNS = [
    "date",
    "location",
    "red_fighter",
    "blue_fighter",
    "weight_class",
    "title_bout",
    "red_Striking Accuracy",
    "blue_Striking Accuracy",
    "red_Defense",
    "blue_Defense",
    "red_Takedown Accuracy",
    "blue_Takedown Accuracy",
    "red_Takedown Defense",
    "blue_Takedown Defense",
    "red_Stance",
    "blue_Stance",
    "red_DOB",
    "blue_DOB",
    "red_Height",
    "blue_Height",
    "red_Reach",
    "blue_Reach",
    "red_record",
    "blue_record",
]
# Column name mappings for next event data
NEXT_EVENT_COLUMN_MAPPING = {
    "red_Striking Accuracy": "red_sig_str_average",
    "blue_Striking Accuracy": "blue_sig_str_average",
    "red_Defense": "red_sig_strike_defence_average",
    "blue_Defense": "blue_sig_strike_defence_average",
    "red_Takedown Accuracy": "red_td_average",
    "blue_Takedown Accuracy": "blue_td_average",
    "red_Takedown Defense": "red_td_defence_average",
    "blue_Takedown Defense": "blue_td_defence_average",
    "red_Stance": "red_stance",
    "blue_Stance": "blue_stance",
}

# Derived column sets
INFERENCE_COLUMNS = BASE_COLUMNS + STAT_COLUMNS
TRAINING_COLUMNS = INFERENCE_COLUMNS + ["winner"]
UFC_KEY_COLUMNS = BASE_COLUMNS + RAW_DATA_COLUMNS
