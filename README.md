Preparation
-----------
This is written for Python 3.  It will not work with the Python 2.7 that comes with Macs.
Mac users can install Python 3 using brew.

(Below, the 'pip' command might actually be 'pip3' on your system.)

    pip install --user lxml cssselect pprint selenium unidecode google-api-python-client \
        pycurl bs4 chardet editdistance
     
    # pdfminer installs the pdf2txt.py command
    pip install pdfminer

install selenium Gecko and Chrome drivers from:
https://github.com/mozilla/geckodriver/releases
https://sites.google.com/a/chromium.org/chromedriver/downloads

Download 'google_api_client_secret.json' into your working directory

Running
-------
There isn't a single command that'll do everything.  The project is a collection of functions 
intended to be run interactively.

However, for a simple demo you can run ./scraper.py without any parameters.