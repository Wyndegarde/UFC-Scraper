import numpy as np
import re

from .abstract import CleanerABC
from ..constants import WEIGHT_CLASS_PATTERN


class CoreCleaner(CleanerABC):
    def clean(self):
        """
        Execute the general cleaning operations on the DataFrame.
        For columns that don't warrant a more specific cleaner.
        """
        self._clean_col_names()
        self._clean_weight_class()
        self._clean_stance()
        return self.df

    def _clean_stance(self) -> None:
        """
        Fill missing stance values with 'Orthodox' for both blue and red corners.
        Orthodox is the most common stance.
        """
        self.df["blue_stance"].replace(np.nan, "Orthodox", inplace=True)
        self.df["red_stance"].replace(np.nan, "Orthodox", inplace=True)

    def _clean_weight_class(self) -> None:
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
