import logging
import os


def get_logger(name: str) -> logging.Logger:
    """
    Creates a standardized application logger.

    This ensures consistent logging format across
    all modules and environments.
    """

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    return logging.getLogger(name)
