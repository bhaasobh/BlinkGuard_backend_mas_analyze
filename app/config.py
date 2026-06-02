import logging
import os

from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("blinkguard.startup")

logger.info("Import complete, loading environment variables")
load_dotenv()
logger.info("Environment loaded")

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")


def get_port() -> int:
    return int(os.getenv("PORT", 3000))
