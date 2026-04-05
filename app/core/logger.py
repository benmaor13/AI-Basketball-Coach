import logging

def get_logger(name: str) -> logging.Logger:
    """
    Helper function to get a logger with the given name.
    """
    # prevents duplicates
    logger = logging.getLogger(name)
    if not logger.handlers:
        # standard output (terminal/console)
        handler = logging.StreamHandler()
        # the format
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger