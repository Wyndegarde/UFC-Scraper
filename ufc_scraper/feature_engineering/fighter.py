from collections import defaultdict
import pandas as pd


class Fighter:
    def __init__(self, full_ufc_df: pd.DataFrame, fighter_name: str) -> None:
        self.full_ufc_df = full_ufc_df
        self.fighter_name = fighter_name
        self.fighter_df = self._get_fighter_df()

    def _get_fighter_df(self) -> pd.DataFrame:
        return self.full_ufc_df[
            (self.full_ufc_df["red_fighter"] == self.fighter_name)
            | (self.full_ufc_df["blue_fighter"] == self.fighter_name)
        ].sort_values(by="date", ascending=True)

    def populate_fighter_df(self):
        ...
    
    def order_fighter_stats(self, stat_cols):
        ordered_fighter_stats = defaultdict(list)
        for _, row in self.fighter_df.iterrows():
            if row["red_fighter"] == self.fighter_name:
                for stat in stat_cols:
                    ordered_fighter_stats[stat].append(row[f"red_{stat}"])
            elif row["blue_fighter"] == self.fighter_name:
                for stat in stat_cols:
                    ordered_fighter_stats[stat].append(row[f"blue_{stat}"])
        
        assert len(ordered_fighter_stats) == 5, "There should be 5 stats per fighter."
        return ordered_fighter_stats
    
    def create_fighter_reg_df(self, ordered_stats):
        lin_reg_df = pd.DataFrame()
        for column, stats in ordered_stats.items():
            lin_reg_df[column] = stats
            x_col, y_col = f"X_{column}", f"Y_{column}"
            lin_reg_df[x_col] =lin_reg_df[column].expanding(2).mean().shift(1)
            lin_reg_df.loc[1, x_col] = lin_reg_df.loc[0, column]
            lin_reg_df[y_col] = lin_reg_df[x_col].shift(1)
            lin_reg_df = lin_reg_df.dropna()


             
