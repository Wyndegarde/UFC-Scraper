from joblib import load
from pathlib import Path
from typing import Any

from sklearn.preprocessing import OrdinalEncoder

from src.lib.processing import CSVProcessingHandler
from .constants import INFERENCE_COLUMNS


class Inference(CSVProcessingHandler):
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
        self.df = self.df.dropna()
        self.df = self.df[INFERENCE_COLUMNS]

        stance_encoder = OrdinalEncoder()
        self.df["red_stance"] = stance_encoder.fit_transform(self.df[["red_stance"]])
        self.df["blue_stance"] = stance_encoder.fit_transform(self.df[["blue_stance"]])

    def predict(self):
        self._prepare_data()
        predictions = self.model.predict(self.df)
        return predictions
