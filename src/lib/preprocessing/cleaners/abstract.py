from abc import ABC, abstractmethod

import pandas as pd


class CleanerABC(ABC):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def clean(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def clean_next_event(self) -> pd.DataFrame:
        pass
