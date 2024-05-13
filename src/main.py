import sys
import logging

import gui

LOG_FILE_LOCATION = "./9gag-scraper.log"
LOG_LEVEL = logging.INFO


def config_logger():
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    file_handler = logging.FileHandler(LOG_FILE_LOCATION)
    file_handler.setLevel(LOG_LEVEL)

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s]\t(%(name)s)\t%(message)s",
        datefmt="%d/%m/%YT%H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    stdout_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    return logger


def main():
    # Init logger
    log = config_logger()

    log.debug("Debug level message")
    log.info("Info level message")
    log.warning("Warning level message")
    log.error("Error level message")
    log.critical("Critical level message")

    log.info("Starting the scraper program")

    my_app = gui.App()
    log.info("Created instance of gui.App")

    try:
        my_app.mainloop()
    finally:
        my_app.close()


if __name__ == "__main__":
    main()
