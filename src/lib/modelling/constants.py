INFERENCE_COLUMNS = [
    "red_stance",
    "blue_stance",
    "height_diff",
    "reach_diff",
    "red_sig_strike_defence_average",
    "blue_sig_strike_defence_average",
    "red_td_defence_average",
    "blue_td_defence_average",
    "red_td_average",
    "blue_td_average",
    "red_sig_str_average",
    "blue_sig_str_average",
]

# Inference columns plus the winner column
TRAINING_COLUMNS = INFERENCE_COLUMNS + ["winner"]
