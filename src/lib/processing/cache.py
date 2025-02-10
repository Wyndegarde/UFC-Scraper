"""
Module to handle the caching of UFC event links processed.
"""

import json

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class CacheABC(ABC):
    @abstractmethod
    def get(self, *args, **kwargs):
        pass

    @abstractmethod
    def write(self, cache: List[str], *args, **kwargs) -> None:
        pass


class JSONCache(CacheABC):
    def __init__(self, cache_file_path: Path):
        self.cache_file_path = cache_file_path

    def get(self) -> List[str]:
        try:
            with open(self.cache_file_path, "r") as f:
                cache = json.load(f)
            return cache
        except FileNotFoundError:
            return []

    def write(self, cache: List[str]) -> None:
        with open(self.cache_file_path, "w") as f:
            json.dump(cache, f)
