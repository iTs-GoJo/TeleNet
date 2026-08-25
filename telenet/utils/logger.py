import logging
_configured = False
def get_logger(name="telenet"):
    global _configured
    if not _configured:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        _configured = True
    return logging.getLogger(name)