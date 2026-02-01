"""Logging."""
import logging
import sys
from src.utils.config import config

def setup_logging():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout, level=getattr(logging, config.log_level))
    return logging.getLogger(__name__)

logger = setup_logging()

