import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOGURU_JSON = os.getenv("LOGURU_JSON", "true").lower() == "true"
LOGS_DIR = "logs"

os.makedirs(LOGS_DIR, exist_ok=True)

logger.remove()
logger.add(
    f"{LOGS_DIR}/tasuke.log",
    rotation="00:00",
    retention="90 days",
    level=LOG_LEVEL,
    serialize=LOGURU_JSON,
    enqueue=True
) 