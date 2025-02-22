from abc import ABC, abstractmethod

import pandas as pd


class CleanerABC(ABC):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def clean(self):
        pass

    @abstractmethod
    def clean_next_event(self):
        pass
