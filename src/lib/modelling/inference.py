from joblib import load
from pathlib import Path
from typing import Any

from sklearn.preprocessing import OrdinalEncoder

from src.lib.abstract import DataFrameABC
from .constants import INFERENCE_COLUMNS


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
        self.object_df = self.object_df[INFERENCE_COLUMNS]

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
