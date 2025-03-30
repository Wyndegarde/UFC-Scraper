from .abstract import CleanerABC
from ..constants import WEIGHT_CLASS_PATTERN
from src.lib.constants.columns import (
    NEXT_EVENT_KEY_COLUMNS,
    NEXT_EVENT_COLUMN_MAPPING,
)


class CoreCleaner(CleanerABC):
    def clean(self):
        """
        Execute the general cleaning operations on the DataFrame.
        For columns that don't warrant a more specific cleaner.
        """
        # Data source represent no attempts as "---".
        self.df.replace("---", "0", inplace=True)
        self._clean_col_names()

        return self.df

    def clean_next_event(self):
        self.clean_next_event_col_names()
        return self.df

    def _clean_col_names(self) -> None:
        """
        Standardise column names by converting to lowercase and replacing
        periods and spaces with underscores.
        """
        self.df.columns = self.df.columns.str.lower()
        self.df.columns = self.df.columns.str.replace(".", "").str.replace(" ", "_")

    def clean_next_event_col_names(self) -> None:

        self.df = self.df[NEXT_EVENT_KEY_COLUMNS]
        self.df.rename(columns=NEXT_EVENT_COLUMN_MAPPING, inplace=True)
