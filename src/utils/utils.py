import json
from pathlib import Path
from typing import List


def try_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            return None


def get_cache(cache_file_path: Path) -> List[str]:
    try:
        with open(cache_file_path, "r") as f:
            cache = json.load(f)
        return cache
    except FileNotFoundError:
        return []


def write_cache(cache_file_path: Path, cache: List[str]) -> None:
    with open(cache_file_path, "w") as f:
        json.dump(cache, f)
