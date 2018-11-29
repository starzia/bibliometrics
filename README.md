Intro
-----
If you are just looking at this code as an example of how to scrape the web, then I'd recommend you
look at these files:
* `school/*.py`: which scrapes faculty information from ten different schools.  These are each runnable.
* `web_util.py`: which has various utility functions for downloading and parsing pages
* `google_scholar.py`: which uses Selenium to scrape Google Scholar data.
    The `wait_for_captchas` function is especially helpful in detecting three different types of Google captchas.


Prerequisites
-------------
This is written for Python 3.  It will not work with the Python 2.7 that comes with Macs.
Mac users can install Python 3 using brew.

Install the prerequisite packages as follows:

    pip install --user lxml cssselect pprint selenium unidecode google-api-python-client \
        pycurl bs4 chardet editdistance matplotlib pdfminer3k

(Above, the `pip` command might actually be `pip3` on your system, and you may not need the `--user` flag.)

To use the Google Scholar scraper, you must first install selenium Gecko and Chrome drivers from:
https://github.com/mozilla/geckodriver/releases
https://sites.google.com/a/chromium.org/chromedriver/downloads

On RHEL/Centos, you will have to first run
   sudo yum install libcurl-devel
   PYCURL_SSL_LIBRARY=nss pip3 install pycurl

On Mac, you may first have to run
   PYCURL_SSL_LIBRARY=openssl LDFLAGS="-L/usr/local/opt/openssl/lib" CPPFLAGS="-I/usr/local/opt/openssl/include" pip install --no-cache-dir pycurl

Running
-------
There isn't a single command that'll do everything.  The project is a collection of functions 
intended to be run interactively.

For a simple demo you can run

    python school/kellogg.py

A full scrape can be started with `./scraper.py`.  BUT... you'll actually have to look at the
code in `scraper.py` and set the variable `do_reload = True`.

To run an analysis that produces all the plots used in the Latex report then run `./analysis.py`.
This relies on your having previously run a full scrape.


Output
------

`./scraper.py`