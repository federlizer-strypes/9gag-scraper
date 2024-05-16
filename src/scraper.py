import io
import time
import logging
import urlparse

import requests
import bs4

from PIL import Image as PILImage
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


log = logging.getLogger(__name__)


class ScrapedImage(object):
    """
    ScrapedImage is an object that represents a scraped image.

    It is useful to contain both the PIL.Image.Image object and its thumbnail
    without the need to copy the image in different places.
    """

    DEFAULT_THUMBNAIL_SIZE = (128, 128)

    def __init__(self, data, name, thumbnail_size=None):
        # Generate full-sized image
        self.image = PILImage.open(io.BytesIO(data))
        self.name = name
        # Generate its thumbnail, but DO NOT overwrite the original image
        if not thumbnail_size:
            thumbnail_size = ScrapedImage.DEFAULT_THUMBNAIL_SIZE
        self.thumbnail = self.image.copy()
        self.thumbnail.thumbnail(thumbnail_size)

    def save(self, *args, **kwargs):
        """Save the image on disk."""

        return self.image.save(*args, **kwargs)


class NineGagScraper(object):
    """A very badly written 9gag image scraper."""

    BASE_ADDRESS = "https://9gag.com"
    SEARCH_ADDRESS_FORMAT = BASE_ADDRESS + "/search?query={}"

    ONETRUST_ACCEPT_BTN_SELECTOR = "button#onetrust-accept-btn-handler"
    ONETRUST_BANNER_SELECTOR = "div#onetrust-banner-sdk"
    ONETRUST_WAIT_TIMEOUT = 20

    DEFAULT_SEARCH_TERM = "kittens"  # Cause they're cute!
    DEFAULT_SCROLL_COUNT = 2

    IMAGE_URL_PREFIX = "https://img-9gag-fun.9cache.com/photo/"

    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600

    def __init__(self):
        self._driver = webdriver.Chrome()
        self._driver.set_window_size(
                NineGagScraper.WINDOW_WIDTH, NineGagScraper.WINDOW_HEIGHT)
        self._driver.get(NineGagScraper.BASE_ADDRESS)
        self._accept_onetrust_cookies()

    def scrape_images(self, search_term=None):
        """
        Perform the scraping of images and return the results which were found.
        """

        if not search_term:
            search_term = NineGagScraper.DEFAULT_SEARCH_TERM
        search_url = NineGagScraper.SEARCH_ADDRESS_FORMAT.format(search_term)
        self._driver.get(search_url)
        self._scroll_to_bottom(count=NineGagScraper.DEFAULT_SCROLL_COUNT)
        for img_url in self._find_images():
            # Get the name of the file as it is stored in 9GAG
            parsed_url = urlparse.urlparse(img_url)
            img_name = parsed_url.path.rsplit("/", 1)[-1]
            log.info("Downloading image '%s'", img_name)
            res = requests.get(img_url)
            if not res.ok:
                log.warning("Couldn't download '%s'. Response: (%s %s) %s",
                            img_url, res.status_code, res.reason, res.text)
                continue
            image = ScrapedImage(res.content, img_name)
            log.info("Successfully downloaded '%s'", img_url)
            yield image

    def _accept_onetrust_cookies(self, timeout=20):
        """
        Accept onetrust's cookies and wait for the banner to be invisible.
        """

        onetrust_btn = (
                By.CSS_SELECTOR,
                NineGagScraper.ONETRUST_ACCEPT_BTN_SELECTOR)
        onetrust_banner = (
                By.CSS_SELECTOR,
                NineGagScraper.ONETRUST_BANNER_SELECTOR)
        # Wait for the accept button to be clickable
        btn_appear_wait = WebDriverWait(self._driver, timeout)
        btn_appear_wait.until(
            expected_conditions.element_to_be_clickable(onetrust_btn)).click()
        # Now wait for the banner to disappear
        banner_disappear_wait = WebDriverWait(self._driver, timeout)
        banner_disappear_wait.until(
            expected_conditions.invisibility_of_element(onetrust_banner))

    def _scroll_to_bottom(self, count=1):
        """Scroll to the bottom of the web page count times."""

        html_elem = self._driver.find_element_by_tag_name("html")
        for _ in range(count):
            log.debug("Scrolling selenium to bottom of page")
            html_elem.send_keys(Keys.END)
            # TODO - try and find a better way to wait for the scroll to finish
            time.sleep(2)

    def _find_images(self):
        """Find the images in the web page that are a part of a post."""

        soup = bs4.BeautifulSoup(self._driver.page_source, "html.parser")
        for img in soup.findAll("img"):
            if NineGagScraper.IMAGE_URL_PREFIX in img["src"]:
                yield img["src"]

    def close(self):
        """Close and cleanup the scraper."""

        self._driver.quit()
