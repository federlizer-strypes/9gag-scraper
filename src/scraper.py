import io
import time
import logging
import urlparse

import requests

from bs4 import BeautifulSoup
from PIL import Image

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


log = logging.getLogger(__name__)


class ScrapedImage(object):
    """ScrapedImage is an object that represents a scraped image. It is useful
    to contain both the PIL.Image.Image object and its thumbnail without the
    need to copy the image in different places.

    Parameters:
        data (bytes): The data that can be used to construct the image

        thumbnail_size (tuple[int], optional): The size of the thumbnail
            that should be generated. Default: (128, 128).
    """

    def __init__(self, data, name, thumbnail_size=(128, 128)):
        # Generate full-sized image
        self._image = Image.open(io.BytesIO(data))
        self._name = name

        # Generate its thumbnail, but DO NOT overwrite the original image
        self._thumbnail = self._image.copy()
        self._thumbnail.thumbnail(thumbnail_size)

    @property
    def image(self):
        """The full-sized image"""
        return self._image

    @property
    def thumbnail(self):
        """The thumbnail of the image"""
        return self._thumbnail

    def save(self, *args, **kwargs):
        return self._image.save(*args, **kwargs)


class NineGagScraper(object):
    """
    A very badly written 9gag image scraper
    """

    BASE_ADDRESS = "https://9gag.com"
    SEARCH_ADDRESS_FORMAT = BASE_ADDRESS + "/search?query={}"

    def __init__(self):
        self._driver = webdriver.Chrome()
        self._driver.set_window_size(800, 600)
        self._driver.get(NineGagScraper.BASE_ADDRESS)
        self._accept_onetrust_cookies()

    def scrape_images(self, tag="kittens"):
        search_url = NineGagScraper.SEARCH_ADDRESS_FORMAT.format(tag)
        self._driver.get(search_url)

        self._scroll_to_bottom(count=2)

        image_urls = self._find_images()

        # Generate PIL image objects
        images = []
        for url in image_urls:
            # Get the name of the file as it is stored in 9GAG
            parsed_url = urlparse.urlparse(url)
            img_name = parsed_url.path.rsplit("/", 1)[-1]

            log.info("Downloading image '%s'", img_name)
            res = requests.get(url)

            if not res.ok:
                log.warning(
                    "Couldn't download '%s'. Response: (%s %s) %s",
                    url,
                    res.status_code,
                    res.reason,
                    res.text)
                continue

            image = ScrapedImage(res.content, img_name)
            images.append(image)
            log.info("Successfully downloaded '%s'", url)

        return images

    def _accept_onetrust_cookies(self, timeout=20):
        """
        Accept onetrust's cookies and wait for the banner to be invisible.
        """

        WebDriverWait(self._driver, timeout) \
            .until(expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, "button#onetrust-accept-btn-handler")
            )).click()

        WebDriverWait(self._driver, timeout) \
            .until(expected_conditions.invisibility_of_element(
                (By.CSS_SELECTOR, "div#onetrust-banner-sdk")
            ))

    def _scroll_to_bottom(self, count=1):
        """
        Scroll to the bottom of the web page. Can provide a count kwarg which
        defines the number of times the scroll will occur.
        """

        html_elem = self._driver.find_element_by_tag_name("html")

        for _ in range(count):
            log.debug("Scrolling selenium to bottom of page")
            html_elem.send_keys(Keys.END)
            # TODO - try and find a better way to wait for the scroll to finish
            time.sleep(2)

    def _find_images(self):
        """
        Find the images in the web page that start with a particular domain
        name (TODO).
        """

        images = []
        soup = BeautifulSoup(self._driver.page_source, "html.parser")
        for img in soup.findAll("img"):
            if "https://img-9gag-fun.9cache.com/photo/" in img["src"]:
                images.append(img["src"])

        return images

    def close(self):
        self._driver.quit()
