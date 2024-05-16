import sys
import logging

import controller


LOG_FILE_LOCATION = "./9gag-scraper.log"
LOG_LEVEL = logging.INFO

log = logging.getLogger()


def main():
    # Config logger
    log.setLevel(LOG_LEVEL)
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
    log.addHandler(file_handler)
    log.addHandler(stdout_handler)
    # Start application
    ctrlr = controller.Controller()
    ctrlr.run()


if __name__ == "__main__":
    main()
