# 9GAG Scraper

A simple 9GAG scraper that uses selenium's Chromium webdriver. It allows you to scrape the images given a particular
search term. The application is written in Python 2.7 with Tkinter 8.6.

## Installation

#### Tkinter
First, you will need to manually install Tkinter. To install it, follow the instructions from the
[tkdocs.com installation tutorial](https://tkdocs.com/tutorial/install.html) webpage. Remember to follow the correct
instructions to install Tkinter for Python 2.7

#### Chromium webdriver

The scraper also uses selenium's Chromium webdriver. I suspect that using a normal Chrome webdriver is going to work
just the same, but I was unable to test it out, since I cannot install pure Chrome webdriver on Linux (whoops). Follow
the instructions from [this webpage](https://chromedriver.chromium.org/getting-started).

#### Pip packages

Finally, you need to install the pip packages that are required for the application to run. It's recommended to create
a virtual environment, so you can separate the installed packages from your global packages:

```bash
# Create a virtual environment
virtualenv ./venv

# Activate the virtual environment for your current shell
source ./venv/bin/activate

# Finally, install the packages from the requirements.txt file
pip install -r ./requirements.txt

# When you're done using the application, you can deactivate the virtual environment
deactivate
```

### Usage

To start the application, you just need to execute the `main.py` script:

```bash
python ./src/main.py
```

This will open up the GUI application, where you'll be able to define the search term you want to scrape with. Hitting
the "Scrape!" button (or enter) will start the scraping process - the webdriver will fetch the webpage needed, scroll
down the required amount (twice by default) and fetch all images that have been found. The images that have been found
will be displaed as thumbnails and you will have the opportunity to save the images on your computer.

### Next steps

- Hit enter to Scrape!
- Make the gui nice looking with some padding between elements
- Get the webdriver to minimize
- Have "Save" buttons below each of the images to be able to save them to a directory
- Have an entry where the user can define the download folder (otherwise, use the default)
- Have an entry field that allows the user to select the number of times the webdriver will scroll down
- Try and find a way to use the `with` keyword with the scraper and gui classes, so the browser can be closed
  nicely without the try/finally clause
- Have some CLI arguments about logging level, logging location, more?
