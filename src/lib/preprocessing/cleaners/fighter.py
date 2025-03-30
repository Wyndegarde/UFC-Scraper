import re
import numpy as np
import pandas as pd
from .abstract import CleanerABC
from ..constants import WEIGHT_CLASS_PATTERN
from src.lib.constants.columns import Columns


class FighterCleaner(CleanerABC):
    def clean(self) -> pd.DataFrame:
        self.clean_stance()
        self.clean_weight_class()
        self.clean_record()
        return self.df

    def clean_next_event(self):
        raise NotImplementedError("FighterCleaner does not support next event cleaning")

    def clean_stance(self) -> None:
        """
        Fill missing stance values with 'Orthodox' for both blue and red corners.
        Orthodox is the most common stance.
        """
        self.df[Columns.BLUE_STANCE].replace(np.nan, "Orthodox", inplace=True)
        self.df[Columns.RED_STANCE].replace(np.nan, "Orthodox", inplace=True)

    def clean_weight_class(self) -> None:
        """
        Clean weight class strings by removing extraneous text using regex pattern.
        Keeps only the weight divisions.
        """
        pattern: re.Pattern = re.compile(WEIGHT_CLASS_PATTERN)
        self.df[Columns.WEIGHT_CLASS] = self.df[Columns.WEIGHT_CLASS].apply(
            lambda x: pattern.sub("", x).strip()
        )
        # remove any rows where weight class is empty string
        self.df = self.df[self.df[Columns.WEIGHT_CLASS] != ""]
        print(self.df[Columns.WEIGHT_CLASS].unique())

    def clean_record(self) -> None:
        """
        Clean the record column by removing the "(record)" text.
        """
        columns_to_clean = {
            Columns.RED_RECORD: (Columns.RED_WINS, Columns.RED_LOSSES),
            Columns.BLUE_RECORD: (Columns.BLUE_WINS, Columns.BLUE_LOSSES),
        }
        for record_column, (wins_column, losses_column) in columns_to_clean.items():
            self.df[wins_column] = (
                self.df[record_column].str.split("-").str[0].astype(int)
            )
            self.df[losses_column] = (
                self.df[record_column].str.split("-").str[1].astype(int)
            )
        self.df.drop(columns=[Columns.RED_RECORD, Columns.BLUE_RECORD], inplace=True)
