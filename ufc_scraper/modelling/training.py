"""
This is an early iteration.
Very basic just to have some form of output but nothing that works with any degree of accuracy
Same with Inference.py

"""
from joblib import dump
from pathlib import Path

import mlflow
from sklearn.preprocessing import OrdinalEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


from ufc_scraper.base_classes import DataFrameABC
from ufc_scraper.config import PathSettings


class Training(DataFrameABC):
    def __init__(self, csv_path: Path, allow_creation: bool = False) -> None:
        super().__init__(csv_path, allow_creation)

    def _prepare_data(self):
        self.object_df = self.object_df[
            (self.object_df.winner != "NC") & (self.object_df.winner != "D")
        ]

        self.object_df = self.object_df.dropna()

        self.object_df = self.object_df.drop(
            columns=[
                "red_fighter",
                "blue_fighter",
                "date",
                "red_age",
                "blue_age",
                "red_sub_att",
                "blue_sub_att",
                "red_total_str_average",
                "blue_total_str_average",
            ]
        )
        self.object_df = self.object_df[
            self.object_df.columns.drop(list(self.object_df.filter(regex="percent")))
        ]

        # one hot encode winner column
        winner_encoder = OrdinalEncoder()
        self.object_df["outcome"] = winner_encoder.fit_transform(
            self.object_df[["winner"]]
        )

        # Drop winner column
        self.object_df = self.object_df.drop(columns=["winner"])

        # one hot encode stance columns
        stance_encoder = OrdinalEncoder()
        self.object_df["red_stance"] = stance_encoder.fit_transform(
            self.object_df[["red_stance"]]
        )
        self.object_df["blue_stance"] = stance_encoder.fit_transform(
            self.object_df[["blue_stance"]]
        )

    def train_model(self):
        self._prepare_data()
        # mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.sklearn.autolog()
        print(self.object_df.columns)
        X = self.object_df.drop(columns=["outcome"], axis=1)
        y = self.object_df["outcome"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        random_forest = RandomForestClassifier(
            random_state=42, max_depth=5, n_estimators=300, min_samples_split=5
        )

        random_forest.fit(X_train, y_train)

        dump(random_forest, PathSettings.MODEL_WEIGHTS)
