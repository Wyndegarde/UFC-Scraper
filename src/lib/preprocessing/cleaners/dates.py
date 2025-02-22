import pandas as pd

from .abstract import CleanerABC


class DateCleaner(CleanerABC):
    def clean(self): ...
