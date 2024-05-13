import os
import logging

from Tkinter import Frame, Label, Entry, Button, StringVar, N, W, E, S
from PIL import ImageTk

import scraper

DOWNLOAD_DIRECTORY = "./images/"

log = logging.getLogger(__name__)


class App(Frame):
    def __init__(self, master=None):
        log.info("Initializing TKinter application")

        # Init scraper
        self.scraper = scraper.NineGagScraper()
        # self.scraper = None

        Frame.__init__(self, master)
        self.master.title("9GAG Scraper")
        self.grid(column=0, row=0, sticky=(N, W, E, S))

        self.init_widgets()
        self.config_keybinds()
        self.config_children()

    def init_widgets(self):
        self.search_term = StringVar()
        self.search_term_entry = Entry(self, textvariable=self.search_term)
        self.search_term_entry.grid(column=1, row=0)

        # Do we need to track these really?
        Label(self, text="Search term") \
            .grid(column=0, row=0)
        Button(self, text="Scrape!", command=self.scrape) \
            .grid(column=0, row=1, columnspan=2)

        self.image_container = ImageContainer(master=self)
        self.image_container.grid(column=0, row=2, columnspan=2, sticky=(W, E))

    def config_keybinds(self):
        # Using a lambda here, to avoid having the scrape method require an
        # *args parameter
        self.master.bind("<Return>", lambda ev: self.scrape())

    def config_children(self):
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def scrape(self):
        search_term = self.search_term.get()
        tag = search_term if search_term else None

        if tag:
            scraped_images = self.scraper.scrape_images(tag=tag)
        else:
            scraped_images = self.scraper.scrape_images()

        self.image_container.update_images(scraped_images)

    def close(self):
        if self.scraper:
            self.scraper.close()


class ImageContainer(Frame):
    def __init__(self, master=None, images=[]):
        Frame.__init__(self, master, borderwidth=1, relief="ridge")
        self._images = images
        self._render()

    def _render(self):
        if not self._images:
            label = Label(self, text="It's so empty in here...")
            label.grid(column=0, row=0)

        else:
            for idx, img in enumerate(self._images):
                # TODO: Make it span multple rows!
                image_container = Image(self, img)
                image_container.grid(column=idx, row=0)

            for child in self.winfo_children():
                child.grid_configure(padx=5, pady=5)

    def _clear_content(self):
        """
        Clears the contents of the ImageContainer
        """

        for child in self.winfo_children():
            child.destroy()

    def update_images(self, images=[]):
        self._images = images
        self._clear_content()
        self._render()


class Image(Frame):
    def __init__(self, master, image):
        Frame.__init__(self, master)
        self._image = image

        # Create image itself
        self._tk_img = ImageTk.PhotoImage(self._image.thumbnail)
        self._tk_img_label = Label(self, image=self._tk_img)
        self._tk_img_label.image = self._tk_img
        self._tk_img_label.grid(column=0, row=0)

        self._save_button = Button(self, text="Save", command=self.save_image)
        self._save_button.grid(column=0, row=1)

    def save_image(self):
        # Ensure the SAVE_LOCATION directory actually exists
        log.info("Saving image {}".format(self._image))

        if not os.path.exists(DOWNLOAD_DIRECTORY):
            os.makedirs(DOWNLOAD_DIRECTORY)

        save_location = "{}/{}".format(DOWNLOAD_DIRECTORY, self._image._name)
        self._image.save(save_location)
        log.info("Successfully saved image {} to {}".format(
            self._image, save_location))
        self._save_button.config(state="disabled", text="Saved")
