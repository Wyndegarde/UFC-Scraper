import re
from ufc_scraper.base_classes import DataFrameABC


class DataCleaningHandler(DataFrameABC):
    def __init__(self, csv_path: str, allow_creation: bool = False) -> None:
        super().__init__(csv_path, allow_creation)
        self.placeholder = "placeholder"

    def _clean_weight_class(self):
        pattern = re.compile(
            r"\d+|Tournament|Interim |UFC \
                |Australia |UK |vs. |Brazil |China \
                    |TUF Nations Canada |America |Latin \
                        |Ultimate Fighter  |Ultimate Fighter "
        )
        self.object_df["weight_class"] = self.object_df["weight_class"].apply(
            lambda x: pattern.sub("", x)
        )

    def _display_total_placeholder_values(self):
        drop_columns = []
        # Will drop the rows with missing days of birth for now. Return to this and investigate
        for column in self.object_df.columns:
            if len(self.object_df[column][self.object_df[column] == "--"]) > 0:
                print(
                    column, len(self.object_df[column][self.object_df[column] == "--"])
                )
            if len(self.object_df[column][self.object_df[column] == "---"]) > 0:
                drop_columns.append(column)
                print(
                    column, len(self.object_df[column][self.object_df[column] == "---"])
                )
