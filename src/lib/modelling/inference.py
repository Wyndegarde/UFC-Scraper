from joblib import load
from pathlib import Path
from typing import Any, List, Dict

from sklearn.preprocessing import OrdinalEncoder

from src.lib.data_managers import CSVProcessingHandler
from src.lib.constants.columns import INFERENCE_COLUMNS


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
        # Store fighter names before filtering columns
        self.red_fighters = self.df["red_fighter"].tolist()
        self.blue_fighters = self.df["blue_fighter"].tolist()

        self.df = self.df[INFERENCE_COLUMNS]

        stance_encoder = OrdinalEncoder()
        self.df["red_stance"] = stance_encoder.fit_transform(self.df[["red_stance"]])
        self.df["blue_stance"] = stance_encoder.fit_transform(self.df[["blue_stance"]])

    def predict(self) -> List[Dict[str, str]]:
        self._prepare_data()
        predictions = self.model.predict(self.df)

        results = []
        for red_fighter, blue_fighter, pred in zip(
            self.red_fighters, self.blue_fighters, predictions
        ):
            results.append(
                {
                    "red_fighter": red_fighter,
                    "blue_fighter": blue_fighter,
                    "predicted_winner": red_fighter if pred == 1 else blue_fighter,
                }
            )

        return results
