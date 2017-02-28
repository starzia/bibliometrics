import pycurl
from io import BytesIO
import re
from bs4 import BeautifulSoup

import time
import random


def wait():
    time.sleep(10 + random.uniform(0,3))

# response header handling code adapted from http://pycurl.io/docs/latest/quickstart.html
class HeaderExtractor():
    def __init__(self):
        self.headers = {}

    def __call__(self, header_line):
        # HTTP standard specifies that headers are encoded in iso-8859-1.
        # On Python 2, decoding step can be skipped.
        # On Python 3, decoding step is required.
        header_line = header_line.decode('iso-8859-1')

        # Header lines include the first status line (HTTP/1.x ...).
        # We are going to ignore all lines that don't have a colon in them.
        # This will botch headers that are split on multiple lines...
        if ':' not in header_line:
            return

        # Break the header line into header name and value.
        name, value = header_line.split(':', 1)

        # Remove whitespace that may be present.
        # Header lines include the trailing newline, and there may be whitespace
        # around the colon.
        name = name.strip()
        value = value.strip()

        # Header names are case insensitive.
        # Lowercase name here.
        name = name.lower()

        # Now we can actually record the header name and value.
        self.headers[name] = value

    def get_encoding(self):
        # Figure out what encoding was sent with the response, if any.
        # Check against lowercased header name.
        encoding = None
        if 'content-type' in self.headers:
            content_type = self.headers['content-type'].lower()
            match = re.search('charset=(\S+)', content_type)
            if match:
                encoding = match.group(1)
        if encoding is None:
            # Default encoding for HTML is iso-8859-1.
            # Other content types may have different default encoding,
            # or in case of binary data, may have no encoding at all.
            encoding = 'iso-8859-1'
        return encoding


def get_tree(url):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.FOLLOWLOCATION, True)  # follow redirects
    c.setopt(c.WRITEDATA, buffer)
    timeout = 20
    c.setopt(c.TIMEOUT, timeout)  # overall timeout
    c.setopt(c.CONNECTTIMEOUT, timeout)
    c.setopt(c.ACCEPTTIMEOUT_MS, timeout * 1000)

    c.setopt(c.HTTPHEADER, ['User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'])
    header_extractor = HeaderExtractor()
    c.setopt(c.HEADERFUNCTION, header_extractor)
    # retry the request if it fails
    max_retries = 10
    for i in range(0, max_retries):
        try:
            c.perform()
            break
        except pycurl.error as err:
            if i < max_retries-1:
                print('WARNING: retrying %s after getting [%s] for %s' % (url, err))
            else:
                raise RuntimeError('Could not download '+url)

    if c.getinfo(pycurl.HTTP_CODE) != 200:
        print('WARNING got status code %d' % c.getinfo(pycurl.HTTP_CODE))
    c.close()

    encoding = header_extractor.get_encoding()

    html = buffer.getvalue().decode(encoding)
    buffer.close()
    return BeautifulSoup(html, 'lxml')


def print_tree(tree):
    print(tree.prettify())


def css_select(tree, css_selector):
    return tree.select(css_selector)