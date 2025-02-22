import numpy as np
from .abstract import CleanerABC


class CoreCleaner(CleanerABC):
    def clean(self):
        # Clean the column names
        # self.df.columns = (
        #     self.df.columns.str.replace(".", "").str.replace(" ", "_").str.lower()
        # )
        self._clean_stance()
        return self.df

    def _clean_stance(self):
        self.df["blue_STANCE"].replace(np.nan, "Orthodox", inplace=True)
        self.df["red_STANCE"].replace(np.nan, "Orthodox", inplace=True)
