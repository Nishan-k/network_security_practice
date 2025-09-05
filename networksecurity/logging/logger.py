import logging
import os
from datetime import datetime



# Name format for the logs file:
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"


logs_path = os.path.join(os.getcwd(), "logs")
os.makedirs(logs_path, exist_ok=True)
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)


logging.basicConfig(
    filename = LOG_FILE_PATH,
    format = "[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level = logging.INFO
)


def log_separator(section_name=""):
    """
    Works as a separator for logs.
    """
    separator_line = "-" * 80
    logging.info(f"\n\n{separator_line}")
    if section_name:
        logging.info(f"START OF: {section_name.upper()}")
        logging.info(f"{separator_line}\n")

    
