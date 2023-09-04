"""
Script to store all the configuration variables
"""
from pathlib import Path
import logging


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

    DATA_DIR: Path = BASE_DIR / "data"

    RAW_DATA_CSV: Path =  DATA_DIR /"raw_ufc_data.csv"

    EVENT_CACHE_JSON: Path = DATA_DIR / "event_cache.json"

    FIGHTER_PROFILE_CACHE_CSV: Path = DATA_DIR / "fighter_profile_cache.csv"

    CLEAN_DATA_CSV: Path = DATA_DIR / "clean_ufc_data.csv"

    TRAINING_DATA_CSV: Path = DATA_DIR / "training_data.csv"
