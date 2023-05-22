"""
Script to store all the configuration variables
"""
import os
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
    # TODO: Investigate whether the os.join should be replaced with a Pathlib equivalent.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    RAW_DATA_CSV = os.path.join(BASE_DIR, "data", "raw_ufc_data.csv")

    EVENT_CACHE_CSV = os.path.join(BASE_DIR, "data", "event_cache.csv")

    FIGHTER_PROFILE_CACHE_CSV = os.path.join(
        BASE_DIR, "data", "fighter_profile_cache.csv"
    )

    CLEAN_DATA_CSV = os.path.join(BASE_DIR, "data", "clean_ufc_data.csv")
