from enum import StrEnum


class Columns(StrEnum):
    DATE = "date"
    LOCATION = "location"
    WINNER = "winner"
    TITLE_BOUT = "title_bout"
    RED_FIGHTER = "red_fighter"
    BLUE_FIGHTER = "blue_fighter"
    RED_STANCE = "red_stance"
    BLUE_STANCE = "blue_stance"
    HEIGHT_DIFF = "height_diff"
    REACH_DIFF = "reach_diff"
    RED_SIG_STR_AVERAGE = "red_sig_str_average"
    BLUE_SIG_STR_AVERAGE = "blue_sig_str_average"
    RED_SIG_STR_DEFENCE_AVERAGE = "red_sig_strike_defence_average"
    BLUE_SIG_STR_DEFENCE_AVERAGE = "blue_sig_strike_defence_average"
    RED_TD_AVERAGE = "red_td_average"
    BLUE_TD_AVERAGE = "blue_td_average"
    RED_TD_DEFENCE_AVERAGE = "red_td_defence_average"
    BLUE_TD_DEFENCE_AVERAGE = "blue_td_defence_average"
    RED_SIG_STR_PERCENT = "red_sig_str_percent"
    BLUE_SIG_STR_PERCENT = "blue_sig_str_percent"
    RED_SIG_STR_DEFENCE_PERCENT = "red_sig_strike_defence_percent"
    BLUE_SIG_STR_DEFENCE_PERCENT = "blue_sig_strike_defence_percent"
    RED_TD_PERCENT = "red_td_percent"
    BLUE_TD_PERCENT = "blue_td_percent"
    RED_TD_DEFENCE_PERCENT = "red_td_defence_percent"
    BLUE_TD_DEFENCE_PERCENT = "blue_td_defence_percent"
    RED_AGE = "red_age"
    BLUE_AGE = "blue_age"
    RED_RECORD = "red_record"
    BLUE_RECORD = "blue_record"
    RED_WINS = "red_wins"
    BLUE_WINS = "blue_wins"
    RED_LOSSES = "red_losses"
    BLUE_LOSSES = "blue_losses"
    WEIGHT_CLASS = "weight_class"


FE_Columns = [
    Columns.RED_FIGHTER,
    Columns.BLUE_FIGHTER,
    Columns.WEIGHT_CLASS,
    Columns.RED_STANCE,
    Columns.BLUE_STANCE,
    Columns.HEIGHT_DIFF,
    Columns.REACH_DIFF,
    Columns.RED_AGE,
    Columns.BLUE_AGE,
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

EVENT_DETAILS_COLUMNS = [
    Columns.DATE,
    Columns.LOCATION,
]

FIGHT_INFO_COLUMNS = [
    Columns.TITLE_BOUT,
    Columns.RED_FIGHTER,
    Columns.BLUE_FIGHTER,
    Columns.WINNER,
    Columns.WEIGHT_CLASS,
    Columns.RED_STANCE,
    Columns.BLUE_STANCE,
    Columns.HEIGHT_DIFF,
    Columns.REACH_DIFF,
    Columns.RED_AGE,
    Columns.BLUE_AGE,
    Columns.RED_WINS,
    Columns.BLUE_WINS,
    Columns.RED_LOSSES,
]

STAT_COLUMNS = [
    Columns.RED_SIG_STR_PERCENT,
    Columns.BLUE_SIG_STR_PERCENT,
    Columns.RED_SIG_STR_DEFENCE_PERCENT,
    Columns.BLUE_SIG_STR_DEFENCE_PERCENT,
]
FIGHTER_AVERAGE_COLUMNS = [
    Columns.RED_TD_AVERAGE,
    Columns.BLUE_TD_AVERAGE,
    Columns.RED_TD_DEFENCE_AVERAGE,
    Columns.BLUE_TD_DEFENCE_AVERAGE,
    Columns.RED_SIG_STR_AVERAGE,
    Columns.BLUE_SIG_STR_AVERAGE,
]

# Base columns that are common across different uses
BASE_COLUMNS = [
    "red_fighter",
    "blue_fighter",
    "red_stance",
    "blue_stance",
    "height_diff",
    "reach_diff",
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

INFERENCE_COLUMNS = [
    Columns.WEIGHT_CLASS,
    Columns.TITLE_BOUT,
    Columns.RED_STANCE,
    Columns.BLUE_STANCE,
    Columns.HEIGHT_DIFF,
    Columns.REACH_DIFF,
    Columns.RED_AGE,
    Columns.BLUE_AGE,
    Columns.RED_WINS,
    Columns.RED_LOSSES,
    Columns.BLUE_LOSSES,
    Columns.BLUE_WINS,
    Columns.RED_SIG_STR_AVERAGE,
    Columns.BLUE_SIG_STR_AVERAGE,
    Columns.RED_SIG_STR_DEFENCE_AVERAGE,
    Columns.BLUE_SIG_STR_DEFENCE_AVERAGE,
    Columns.RED_TD_AVERAGE,
    Columns.BLUE_TD_AVERAGE,
    Columns.RED_TD_DEFENCE_AVERAGE,
    Columns.BLUE_TD_DEFENCE_AVERAGE,
]


# Derived column sets
# INFERENCE_COLUMNS = BASE_COLUMNS + STAT_COLUMNS
TRAINING_COLUMNS = INFERENCE_COLUMNS + [Columns.WINNER]
