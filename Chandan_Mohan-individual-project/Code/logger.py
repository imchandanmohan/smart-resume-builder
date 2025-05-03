import logging
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parents[1]
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


LOGS_FILE = LOGS_DIR / f"log_{datetime.now().strftime('%Y-%m-%d')}.log"


logging.basicConfig(
    filename=LOGS_FILE,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO
)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
