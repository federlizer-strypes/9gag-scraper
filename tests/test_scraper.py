import io
import unittest
import mock
import random

from PIL import Image as PILImage

from ninegag_scraper import scraper


IMAGE_TEST_FORMAT = "PNG"
img_1_url = "{}test_img_1.png".format(scraper.NineGagScraper.IMAGE_URL_PREFIX)
img_2_url = "{}test_img_2.png".format(scraper.NineGagScraper.IMAGE_URL_PREFIX)
img_3_url = "{}test_img_3.png".format(scraper.NineGagScraper.IMAGE_URL_PREFIX)


def gen_image():
    """Generate a randomly colored image."""

    red = random.randrange(0, 257)
    green = random.randrange(0, 257)
    blue = random.randrange(0, 257)
    img = PILImage.new('RGBA', size=(50, 50), color=(red, green, blue))
    img_bytes = io.BytesIO()
    img.save(img_bytes, IMAGE_TEST_FORMAT)
    return (img, img_bytes)


def gen_mocked_requests_get(urls):
    """Generate the mocked requests.get function."""

    images = {}
    for url in urls:
        img, img_bytes = gen_image()
        images[url] = {"img": img, "img_bytes": img_bytes}

    def mocked_request_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, content, status_code):
                self.content = content
                self.status_code = status_code

            def ok(self):
                return 200 <= self.status_code <= 299

        if args[0] in images:
            return MockResponse(images[args[0]]["img_bytes"].getvalue(), 200)
        else:
            return MockResponse(None, 404)

    return images, mocked_request_get


def mocked_webelement(*args, **kwargs):
    class MockWebElement:
        def __init__(self, displayed, enabled):
            self.displayed = displayed
            self.enabled = enabled

        def is_displayed(self):
            return self.displayed

        def is_enabled(self):
            return self.enabled

        def click(self):
            pass

    if args[1] == scraper.NineGagScraper.ONETRUST_ACCEPT_BTN_SELECTOR:
        return MockWebElement(True, True)
    elif args[1] == scraper.NineGagScraper.ONETRUST_BANNER_SELECTOR:
        return MockWebElement(False, False)
    else:
        raise Exception(
            "Test asked for unknown web element. Args: {}, Kwargs: {}".format(
                args, kwargs))


def gen_mocked_page_source(imgs):
    """Generate the mocked page_source."""

    img_tags = map(lambda src: "<img src='{}' />".format(src), imgs)
    return """
    <html>
        <body>
            {}
        </body>
    </html>
    """.format("".join(img_tags))


class TestNineGagScraper(unittest.TestCase):

    def setUp(self):
        # Patch selenium.webdriver
        webdriver_patcher = mock.patch("ninegag_scraper.scraper.webdriver")
        webdriver_mock = webdriver_patcher.start()
        self.driver_mock = webdriver_mock.Chrome()
        self.driver_mock.find_element.side_effect = mocked_webelement
        # Patch requests.get
        get_patcher = mock.patch("ninegag_scraper.scraper.requests.get")
        self.get_mock = get_patcher.start()
        # Patch time.sleep
        sleep_patcher = mock.patch("ninegag_scraper.scraper.time.sleep")
        sleep_patcher.start()
        # Ensure cleanup happens!
        self.addCleanup(webdriver_patcher.stop)
        self.addCleanup(get_patcher.stop)
        self.addCleanup(sleep_patcher.stop)
        self.scraper = scraper.NineGagScraper()

    def tearDown(self):
        self.scraper.close()
        self.scraper = None

    def test_scrape_images(self):
        # Setup
        tests = (
            {"urls": [img_1_url, img_2_url, img_3_url], "expected_images": 3},
            {"urls": [img_1_url], "expected_images": 1},
            {"urls": [], "expected_images": 0},
        )

        for tt in tests:
            self.driver_mock.page_source = gen_mocked_page_source(tt["urls"])
            expected_images, mocked_request_get = gen_mocked_requests_get(tt["urls"])
            self.get_mock.side_effect = mocked_request_get

            scraped_images = list(self.scraper.scrape_images())
            self.assertEqual(len(scraped_images), tt["expected_images"])

            for scraped_image in scraped_images:
                img_url = "{}{}".format(
                        scraper.NineGagScraper.IMAGE_URL_PREFIX,
                        scraped_image.name)
                self.assertIn(img_url, expected_images)
                scraped_image_bytes = io.BytesIO()
                scraped_image.image.save(scraped_image_bytes, IMAGE_TEST_FORMAT)
                self.assertEqual(scraped_image_bytes.getvalue(), expected_images[img_url]["img_bytes"].getvalue())


if __name__ == '__main__':
    unittest.main(failfast=False, verbosity=2)
