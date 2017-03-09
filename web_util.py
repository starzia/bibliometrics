import pycurl
from io import BytesIO
import re
from bs4 import BeautifulSoup
from bs4 import Tag
from typing import List

import time
import random
import urllib
import chardet
import json


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


def get_bytes(url) -> bytes:
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
                print('WARNING: retrying %s after getting [%s]' % (url, err))
            else:
                raise RuntimeError('Could not download '+url)

    if c.getinfo(pycurl.HTTP_CODE) != 200:
        print('WARNING got status code %d' % c.getinfo(pycurl.HTTP_CODE))
    c.close()

    # NOTE: we check the character encoding in the HTTP headers, but we ignore that because it's often misconfigured
    expected_encoding = header_extractor.get_encoding()

    body_bytes = buffer.getvalue()
    buffer.close()
    return body_bytes


def get_string(url):
    body_bytes = get_bytes(url)
    detected_encoding = chardet.detect(body_bytes)['encoding']
    return body_bytes.decode(detected_encoding)


def get_tree(url):
    return tree_from_string(get_string(url))


def get_json(url):
    return json.loads(get_string(url))


def tree_from_string(string):
    return BeautifulSoup(string, 'lxml')


def print_tree(tree):
    print(tree.prettify())


def css_select(tree, css_selector) -> Tag:
    return tree.select(css_selector)


space_matcher = re.compile(r"\s+")


def strip_whitespace(str):
    if str is None:
        return None
    return space_matcher.sub(' ', str).strip()


class Selector:
    def __init__(self, css_selector):
        self.css_selector = css_selector

    def __call__(self, tree: Tag) -> str:
        try:
            return strip_whitespace(css_select(tree, self.css_selector)[0].text)
        except (IndexError, AttributeError):
            return None


class HrefSelector:
    def __init__(self, css_selector: str, *anchor_text: str):
        """anchor_text can be a list of strings or a single string."""
        self.css_selector = css_selector
        self.anchor_text = anchor_text

    def __call__(self, current_url: str, tree: Tag) -> str:
        for a in css_select(tree, self.css_selector):
            for anchor_text_i in self.anchor_text:
                if anchor_text_i in a.text:
                    return urllib.parse.urljoin(current_url, a.get('href')).replace(' ', '%20')
        return None


class ListSelector:
    def __init__(self, css_selector: str):
        self.css_selector = css_selector

    def __call__(self, tree: Tag) -> List[str]:
        try:
            return [strip_whitespace(e.text) for e in css_select(tree, self.css_selector)]
        except (IndexError, AttributeError):
            return None


class HrefListSelector:
    def __init__(self, css_selector):
        self.css_selector = css_selector

    def __call__(self, current_url: str, tree: Tag) -> List[str]:
        urls = []
        for e in css_select(tree, self.css_selector):
            if e.get('href') is not None:
                urls.append(urllib.parse.urljoin(current_url, e.get('href').strip()))
        return urls