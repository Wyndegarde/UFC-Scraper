"""
Script to store all the configuration variables
"""

from pathlib import Path
import logging
from rich.console import Console


console = Console()


class Config:
    """
    This class will hold all the configuration variables.
    """

    # Loguru parameters
    level = logging.DEBUG
    rotation = "100 MB"
    scraper_log = "logs/scraper.log"
    format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "file: <cyan>{file}</cyan> -> path: <cyan>{name}</cyan> -> function: <cyan>{function}</cyan> -> line: <cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )


class PathSettings:
    """
    This class will hold all the paths to the data files.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    TEST_DIR: Path = BASE_DIR.parent / "tests"

    DATA_DIR: Path = BASE_DIR.parent / "data"

    RAW_DATA_CSV: Path = DATA_DIR / "raw_ufc_data.csv"

    EVENT_CACHE_JSON: Path = DATA_DIR / "event_cache.json"

    FIGHTER_PROFILE_CACHE_CSV: Path = DATA_DIR / "fighter_profile_cache.csv"

    CLEAN_DATA_CSV: Path = DATA_DIR / "clean_ufc_data.csv"

    TRAINING_DATA_CSV: Path = DATA_DIR / "training_data.csv"

    NEXT_EVENT_CSV: Path = DATA_DIR / "next_event.csv"

    MODEL_WEIGHTS: Path = DATA_DIR / "model_weights.joblib"

    TEST_PAGES: Path = TEST_DIR / "html_pages"

    TEST_FIGHTER_PROFILE: Path = TEST_PAGES / "fighter_profile.html"
