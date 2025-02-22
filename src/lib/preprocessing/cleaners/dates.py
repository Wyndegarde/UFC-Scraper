import pandas as pd
from datetime import datetime

from .abstract import CleanerABC


class DateCleaner(CleanerABC):
    def clean(self) -> pd.DataFrame:
        """
        Execute the complete date cleaning process.
        """
        self._format()
        self._create_age_columns()
        return self.df

    def clean_next_event(self):
        pass

    def _format(self):
        """
        Format date columns to datetime objects.
        - Converts event date column to 'Month DD, YYYY' format
        - Removes rows where fighter DOB is missing ('--') as these rows can't be estimated.
        - Converts DOB columns to 'Month DD, YYYY' format
        """
        self.df["date"] = self.df["date"].apply(
            lambda x: datetime.strptime(x, "%B %d, %Y")
        )
        self.df.drop(self.df[self.df["blue_dob"] == "--"].index, inplace=True)
        self.df.drop(self.df[self.df["red_dob"] == "--"].index, inplace=True)
        for column in self.df.columns:
            if "dob" in column:
                self.df[column] = self.df[column].apply(
                    lambda x: datetime.strptime(x, "%b %d, %Y")
                )

    def _create_age_columns(self):
        """
        Calculate each fighter's age at the time of their fight.
        """
        self.df["red_age"] = (
            self.df["date"]
            .sub(self.df["red_dob"])
            .dt.days.div(365.25)
            .round(0)
            .astype(int)
        )
        self.df["blue_age"] = (
            self.df["date"]
            .sub(self.df["blue_dob"])
            .dt.days.div(365.25)
            .round(0)
            .astype(int)
        )
