UFC_KEY_COLUMNS = [
    "date",
    "red_fighter",
    "blue_fighter",
    "winner",
    "red_sig_str_percent",
    "blue_sig_str_percent",
    "red_sub_att",
    "blue_sub_att",
    "red_stance",
    "blue_stance",
    "red_total_str_percent",
    "blue_total_str_percent",
    "red_td_percent",
    "blue_td_percent",
    "height_diff",
    "reach_diff",
    "red_age",
    "blue_age",
    "red_sig_strike_defence_percent",
    "blue_sig_strike_defence_percent",
    "red_td_defence_percent",
    "blue_td_defence_percent",
]


# Lazy way of doing this rn. cba finding more elegant solution.
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

WEIGHT_CLASS_PATTERN = r"\d+|Tournament|Interim |UFC \
                |Australia |UK |vs. |Brazil |China \
                    |TUF Nations Canada |America |Latin \
                        |Ultimate Fighter  |Ultimate Fighter "
