from typing import List, Tuple, Dict
import pandas as pd

from .abstract import CleanerABC


class StatsCleaner(CleanerABC):
    def clean(self) -> pd.DataFrame:
        self._handle_attempt_landed_columns()
        self._handle_percent_columns()
        return self.df

    """-----------------------------------Attempted and landed columns-----------------------------------"""

    def _handle_attempt_landed_columns(self) -> None:
        """
        Breaks up the columns where the values are strings like "x of y".
        """
        attempt_landed_columns: List[str] = self._get_attempt_landed_columns()

        for column in attempt_landed_columns:
            attempted, landed = self._split_attempt_landed_column(column)
            self._create_stat_columns(column, attempted, landed)
            self.df.drop(columns=column, inplace=True)

    def _split_attempt_landed_column(self, column: str) -> Tuple[pd.Series, pd.Series]:
        """Split a 'x of y' column into attempted and landed series."""
        splitting_column: pd.DataFrame = self.df[column].str.split(" of ", expand=True)
        attempted: pd.Series = splitting_column[1].astype(float)
        landed: pd.Series = splitting_column[0].astype(float)
        return attempted, landed

    def _create_stat_columns(
        self, original_column: str, attempted: pd.Series, landed: pd.Series
    ) -> None:
        """Create attempted, landed, and percentage columns from the supplied column name and data."""
        column_suffixes: Dict[str, str] = {
            "attempted": f"{original_column}_attempted",
            "landed": f"{original_column}_landed",
            "percent": f"{original_column}_percent",
        }

        self.df[column_suffixes["attempted"]] = attempted
        self.df[column_suffixes["landed"]] = landed
        self.df[column_suffixes["percent"]] = self._calculate_percentage(
            landed, attempted
        )

    def _calculate_percentage(
        self, numerator: pd.Series, denominator: pd.Series
    ) -> pd.Series:
        """Calculate percentage and handle division by zero."""
        return (numerator / denominator).fillna(0)

    """-----------------------------------Percentage columns-----------------------------------"""

    def _handle_percent_columns(self) -> None:
        """Handle percentage columns and calculate defense percentages."""
        self._convert_percent_strings_to_float()
        self._calculate_defense_percentages()

    def _convert_percent_strings_to_float(self) -> None:
        """Convert percentage strings (e.g., '75%') to float values (0.75)."""
        percent_cols: List[str] = [col for col in self.df.columns if "%" in col]
        for column in percent_cols:
            self.df[column] = self.df[column].str.strip("%").astype("float") / 100

    def _calculate_defense_percentages(self) -> None:
        """Calculate strike and takedown defense percentages for both fighters."""
        defense_calculations: Dict[str, str] = {
            "red_sig_strike_defence_percent": "blue_sig_str_%",
            "blue_sig_strike_defence_percent": "red_sig_str_%",
            "red_td_defence_percent": "blue_td_%",
            "blue_td_defence_percent": "red_td_%",
        }

        for new_col, source_col in defense_calculations.items():
            self.df[new_col] = 1 - self.df[source_col]

    def _get_attempt_landed_columns(self) -> List[str]:
        """
        Finds all columns where the values look like "x of y"
        """
        attempt_landed_columns: List[str] = []

        # Separated out conditions for clarity.
        for column in self.df.columns:
            # Ensure the column is a string column.
            type_condition: bool = self.df[column].dtype == object

            # Ensure at least one of the values contains "of".
            of_condition: bool = (
                sum(self.df[column].apply(lambda x: "of" in str(x))) > 0
            )

            # Some fighters can have "of" in their name. Don't want that
            name_condition: bool = "fighter" not in column.lower()

            if type_condition and of_condition and name_condition:
                attempt_landed_columns.append(column)

        return attempt_landed_columns
