from joblib import load
from pathlib import Path
from typing import Any

from sklearn.preprocessing import OrdinalEncoder

from ufc_scraper.base_classes import DataFrameABC


class Inference(DataFrameABC):
    """
    Class for making predictions on new data using trained model.
    """

    def __init__(
        self,
        model_weights: Any,
        csv_path: Path,
        allow_creation: bool = False,
    ) -> None:
        super().__init__(csv_path, allow_creation)

        self.model = load(model_weights)

    def _prepare_data(self):
        self.object_df = self.object_df.dropna()
        self.object_df.rename(
            columns={
                "Height_diff": "height_diff",
                "Reach_diff": "reach_diff",
            },
            inplace=True,
        )
        self.object_df = self.object_df[
            [
                "red_stance",
                "blue_stance",
                "height_diff",
                "reach_diff",
                "red_sig_strike_defence_average",
                "blue_sig_strike_defence_average",
                "red_td_defence_average",
                "blue_td_defence_average",
                "red_td_average",
                "blue_td_average",
                "red_sig_str_average",
                "blue_sig_str_average",
            ]
        ]

        stance_encoder = OrdinalEncoder()
        self.object_df["red_stance"] = stance_encoder.fit_transform(
            self.object_df[["red_stance"]]
        )
        self.object_df["blue_stance"] = stance_encoder.fit_transform(
            self.object_df[["blue_stance"]]
        )

    def predict(self):
        self._prepare_data()
        predictions = self.model.predict(self.object_df)
        return predictions
