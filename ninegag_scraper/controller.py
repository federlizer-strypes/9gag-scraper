import logging
import os

from . import gui, scraper


log = logging.getLogger(__name__)

IMAGE_SAVE_LOCATION = "./images"


class Controller(object):
    """
    Sets up the whole application and hooks up the different components.
    """

    def __init__(self):
        self._scraper = None
        self._gui = None
        self._setup_gui()
        self._setup_scraper()

    def _setup_gui(self):
        """Setup the GUI and callbacks for it."""

        self._gui = gui.App(self.scrape, self.save_image)
        self._gui.config_bind("<Return>", self.scrape)

    def _setup_scraper(self):
        """Setup the scraper."""

        self._scraper = scraper.NineGagScraper()

    def scrape(self, *args, **kwargs):
        """Scrape images using the scraper instance."""

        search_term = self._gui.get_search_term()
        images = list(self._scraper.scrape_images(search_term))
        self._gui.display_images(images)

    def save_image(self, *args, **kwargs):
        """Save an image to disk."""

        if not args:
            log.warning("""Didn't receive the component that
                        contains the image we need to save""")
            return
        tk_frame = args[0]
        image = tk_frame.image
        # Ensure the IMAGE_SAVE_LOCATION actually exists
        if not os.path.exists(IMAGE_SAVE_LOCATION):
            os.makedirs(IMAGE_SAVE_LOCATION)
            log.info("Created {}".format(IMAGE_SAVE_LOCATION))
        full_path = "{}/{}".format(IMAGE_SAVE_LOCATION, image.name)
        image.save(full_path)
        log.info("Successfully saved image {}".format(full_path))
        tk_frame.disable_save_button()

    def run(self):
        """Run the application."""

        try:
            self._gui.start()
        finally:
            self._scraper.close()
