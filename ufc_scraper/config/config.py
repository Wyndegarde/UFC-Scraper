"""
Script to store all the configuration variables
"""
import logging
from loguru import logger


class Config:
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
