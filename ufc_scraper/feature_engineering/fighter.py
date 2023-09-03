from typing import List, DefaultDict
from collections import defaultdict
import pandas as pd


class Fighter:
    """
    Class responsible for working with a single fighter and the stats associated with them.
    Used to create a dataframe containing data which will be used to create a regression model to fill in missing data.
    """
    def __init__(self, full_ufc_df: pd.DataFrame, fighter_name: str) -> None:
        self.full_ufc_df = full_ufc_df
        self.fighter_name = fighter_name
        self.fighter_df = self._get_fighter_df()

    def _get_fighter_df(self) -> pd.DataFrame:
        """
        Returns a dataframe of all fights that the fighter has been in.
        """
        return self.full_ufc_df[
            (self.full_ufc_df["red_fighter"] == self.fighter_name)
            | (self.full_ufc_df["blue_fighter"] == self.fighter_name)
        ].sort_values(by="date", ascending=True)

    def populate_fighter_df(self):
        ...

    def order_fighter_stats(
        self, stat_cols: List[str]
    ) -> DefaultDict[str, List[float]]:
        """
        For a given fighter, all specified stats are extracted in chronological order.
        The stats are then stored in a dictionary where the key is the stat name
        and the value is a list of the stats in chronological order.

        Args:
            stat_cols (List[str]): List of stats to extract.

        Returns:
            DefaultDict[str, List[float]]: Dictionary of stats in chronological order.
        """
        # Default dict is used to avoid having to explicitly specify the initial dictionary
        ordered_fighter_stats: DefaultDict[str, List[float]] = defaultdict(list)

        # DF is ordered by date, so stats are already in chronological order
        # But for the fighter, the stats are in different columns depending on whether they are red or blue corner.
        for _, row in self.fighter_df.iterrows():
            if row["red_fighter"] == self.fighter_name:
                for stat in stat_cols:
                    ordered_fighter_stats[stat].append(row[f"red_{stat}"])
            elif row["blue_fighter"] == self.fighter_name:
                for stat in stat_cols:
                    ordered_fighter_stats[stat].append(row[f"blue_{stat}"])

        # Sanity check on the off chance a fighter df is missing a stat.
        assert len(ordered_fighter_stats) == len(
            stat_cols
        ), "There should be the same number of extracted stats as specified stats."
        return ordered_fighter_stats

    def create_fighter_reg_df(
        self, ordered_stats: DefaultDict[str, List[float]]
    ) -> pd.DataFrame:
        """
        Calculates the x and y columns for each stat and returns a dataframe
        The X column calculates the cumulative average of the stat.
        expanding(2).mean() starts from the second row and calculates the average of the preceeding rows.
        This in effect calculates the average of that stat for the fighter at the point they were going into their next fight.
        so if a fighter had 10 fights, the 10th row will be the average of the previous 9 fights.
        This aspect is handled by the shift(1) method which shifts the column down by 1 row.
        The Y column is in effect the average *after* the fight. 
        So that we are predicting what the average will be after the fight using the average going into the fight.
        Args:
            ordered_stats (DefaultDict[str, List[float]]): A dictionary holding all the available stats for a fighter.

        Returns:
            pd.DataFrame: a dataframe with the x and y columns for each stat for that fighter.
        """
        lin_reg_df = pd.DataFrame()
        for column, stats in ordered_stats.items():
            # Easier to manipulate stats using pandas
            lin_reg_df[column] = stats

            # Create lagged columns for each stat - easier to use
            x_col, y_col = f"X_{column}", f"Y_{column}"
            # 
            lin_reg_df[x_col] = lin_reg_df[column].expanding(2).mean().shift(1)

            #! Return to this as unsure what mypy is moaning about
            lin_reg_df.loc[1, x_col] = lin_reg_df.loc[0, column] # type: ignore
            lin_reg_df[y_col] = lin_reg_df[x_col].shift(1)
            lin_reg_df = lin_reg_df.dropna()
        return lin_reg_df
