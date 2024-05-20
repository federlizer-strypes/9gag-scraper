import unittest

from ninegag_scraper import scraper


class WebElementMock(object):

    def __init__(self, enabled=False, displayed=False):
        self.enabled = enabled
        self.displayed = displayed

    def is_displayed(self):
        return self.displayed

    def is_enabled(self):
        return self.enabled

    def click(self):
        pass

    def send_keys(self, *args, **kwargs):
        pass


class WebdriverMock(object):

    def __init__(self):
        self.page_source = None

    def get(self, url):
        self.page_source = """
        <html>
            <body>
                <img
                    src="https://img-9gag-fun.9cache.com/photo/test_img_1.jpg"
                />
                <img
                    src="https://img-9gag-fun.9cache.com/photo/test_img_2.jpg"
                />
                <img
                    src="https://img-9gag-fun.9cache.com/photo/test_img_3.jpg"
                />
            </body>
        </html>
        """

    def find_element(*args, **kwargs):
        css_selector = args[2]
        if css_selector == "button#onetrust-accept-btn-handler":
            return WebElementMock(enabled=True, displayed=True)
        elif css_selector == "div#onetrust-banner-sdk":
            return WebElementMock(enabled=True, displayed=False)

        raise Exception("Searching for unknown element")

    def find_element_by_tag_name(*args, **kwargs):
        return WebElementMock()

    def quit(self):
        pass


class TestNineGagScraper(unittest.TestCase):
    """Test cases for the NineGagScraper class."""

    def setUp(self):
        self.driver = WebdriverMock()
        self.scraper = scraper.NineGagScraper(self.driver)

    def tearDown(self):
        self.scraper.close()
        self.scraper = None
        self.driver = None

    def test_find_images(self):
        images = list(self.scraper._find_images())
        self.assertEqual(len(images), 3)


if __name__ == '__main__':
    unittest.main()
