from typing import Dict
import numpy as np
import re

from .abstract import CleanerABC
from ..constants import WEIGHT_CLASS_PATTERN, NEXT_EVENT_KEY_COLUMNS


class CoreCleaner(CleanerABC):
    def clean(self):
        """
        Execute the general cleaning operations on the DataFrame.
        For columns that don't warrant a more specific cleaner.
        """
        # Data source represent no attempts as "---".
        self.df.replace("---", "0", inplace=True)
        self._clean_col_names()
        self.clean_weight_class()
        self.clean_stance()
        return self.df

    def clean_next_event(self):
        self.clean_stance()
        self.clean_weight_class()
        return self.df

    def clean_stance(self) -> None:
        """
        Fill missing stance values with 'Orthodox' for both blue and red corners.
        Orthodox is the most common stance.
        """
        self.df["blue_stance"].replace(np.nan, "Orthodox", inplace=True)
        self.df["red_stance"].replace(np.nan, "Orthodox", inplace=True)

    def clean_weight_class(self) -> None:
        """
        Clean weight class strings by removing extraneous text using regex pattern.
        Keeps only the weight divisions.
        """
        pattern: re.Pattern = re.compile(WEIGHT_CLASS_PATTERN)
        self.df["weight_class"] = self.df["weight_class"].apply(
            lambda x: pattern.sub("", x)
        )

    def _clean_col_names(self) -> None:
        """
        Standardise column names by converting to lowercase and replacing
        periods and spaces with underscores.
        """
        self.df.columns = self.df.columns.str.lower()
        self.df.columns = self.df.columns.str.replace(".", "").str.replace(" ", "_")

    def clean_next_event_col_names(self) -> None:
        column_mapper: Dict[str, str] = {
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

        self.df = self.df[NEXT_EVENT_KEY_COLUMNS]
        self.df.rename(columns=column_mapper, inplace=True)
