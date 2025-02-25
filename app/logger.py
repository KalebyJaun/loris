import logging
from logging.handlers import RotatingFileHandler
import sys

log_format = "[%(asctime)s] [%(levelname)s] - %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        RotatingFileHandler("app.log", maxBytes=1000000, backupCount=3), 
        logging.StreamHandler(sys.stdout) 
    ],
)

logger = logging.getLogger("fastapi_app")
