import os
import logging

import Tkinter as tk

from PIL import ImageTk as PILImageTk


DOWNLOAD_DIRECTORY = "./images"

log = logging.getLogger(__name__)


class App(tk.Frame):
    """The TK main application class."""

    TITLE = "9GAG Scraper"
    SEARCH_TERM_LABEL_TEXT = "Search term:"
    SCRAPE_BUTTON_TEXT = "Scrape!"

    def __init__(self, scrape_cb, save_image_cb, master=None):
        tk.Frame.__init__(self, master)
        # Callback functions
        self._scrape_cb = scrape_cb
        self._save_image_cb = save_image_cb
        # TK components
        self._search_term = None
        self._search_term_label = None
        self._search_term_entry = None
        self._scrape_button = None
        self._image_container = None

        self._setup_application()
        self._init_widgets()
        self._position_widgets()

    def _setup_application(self):
        """Setup the application's configuration."""

        self.master.title(App.TITLE)

    def _init_widgets(self):
        """Initialize widgets."""

        self._search_term = tk.StringVar()
        self._search_term_entry = tk.Entry(
                self, textvariable=self._search_term)
        self._search_term_label = tk.Label(
                self, text=App.SEARCH_TERM_LABEL_TEXT)
        self._scrape_button = tk.Button(
                self, text=App.SCRAPE_BUTTON_TEXT, command=self._scrape)
        self._image_container = ImageContainer(
                self._save_image_cb, master=self)

    def _position_widgets(self):
        """Position and pad application widgets."""

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        # First row
        self._search_term_label.grid(column=0, row=0, padx=5, pady=5)
        self._search_term_entry.grid(column=1, row=0, padx=5, pady=5)
        # Second row
        self._scrape_button.grid(column=0, row=1, columnspan=2, padx=5, pady=5)
        # Third row and onwards
        self._image_container.grid(
                column=0, row=2, columnspan=2, sticky=(tk.W, tk.E))

    def _scrape(self):
        """Call scrape callback function."""

        if self._scrape_cb:
            self._scrape_cb()

    def config_bind(self, bind, cb):
        """Configure a keybind to a callback function."""

        self.master.bind(bind, lambda ev: cb(ev))

    def get_search_term(self):
        """Retrieve the search term written by the user."""

        return self._search_term.get()

    def display_images(self, images):
        """Display the images on the GUI."""

        self._image_container.update_images(images)

    def start(self):
        """Start up the TK application."""

        self.mainloop()


class ImageContainer(tk.Frame):
    """A container that displays the images that have been scraped."""

    DEFAULT_RELIEF = "ridge"
    DEFAULT_BORDREWIDTH = 1
    PLACEHOLDER_TEXT = "It's so empty in here..."

    def __init__(self, save_image_cb, master=None, images=None):
        tk.Frame.__init__(
                self, master, borderwidth=ImageContainer.DEFAULT_BORDREWIDTH,
                relief=ImageContainer.DEFAULT_RELIEF)
        self._save_image_cb = save_image_cb
        self._images = images
        self._render()

    def _render(self):
        """Render the images (or the lack thereof)."""

        if not self._images:
            label = tk.Label(self, text=ImageContainer.PLACEHOLDER_TEXT)
            label.grid(column=0, row=0)
            return
        # Render each image in the container
        for idx, img in enumerate(self._images):
            # TODO: Make it span multple rows
            image_container = Image(self, img, self._save_image_cb)
            image_container.grid(column=idx, row=0)
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def _clear_content(self):
        """Clear the contents of the ImageContainer."""

        for child in self.winfo_children():
            child.destroy()

    def update_images(self, images=None):
        """Update the images displayed in the container."""

        self._images = images
        self._clear_content()
        self._render()


class Image(tk.Frame):
    """
    A component that displays an image and a button to save the image to disk.
    """

    ACTIVE_BUTTON_TEXT = "Save"
    DISABLED_BUTTON_TEXT = "Saved"

    def __init__(self, master, image, save_cb):
        tk.Frame.__init__(self, master)
        self._save_cb = save_cb
        self.image = image
        self._tk_img = PILImageTk.PhotoImage(self.image.thumbnail)
        self._tk_img_label = tk.Label(self, image=self._tk_img)
        self._tk_img_label.image = self._tk_img
        self._tk_img_label.grid(column=0, row=0)
        self._save_button = tk.Button(
                self, text=Image.ACTIVE_BUTTON_TEXT, command=self._save)
        self._save_button.grid(column=0, row=1)

    def _save(self):
        """Call the save callback function."""

        if self._save_cb:
            self._save_cb(self)

    def disable_save_button(self):
        """Disable the save button."""

        self._save_button.config(
                state="disabled", text=Image.DISABLED_BUTTON_TEXT)
