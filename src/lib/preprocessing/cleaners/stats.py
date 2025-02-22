from .abstract import CleanerABC


class StatsCleaner(CleanerABC):
    def clean(self): ...
