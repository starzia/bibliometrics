import lxml.html
from lxml.cssselect import CSSSelector
import pycurl
from io import BytesIO

import time
import random

def wait():
    time.sleep(3 + random.uniform(0,3))

def get_tree(url):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    html = str(buffer.getvalue())
    return lxml.html.fromstring(html)

def print_tree(tree):
    print(lxml.etree.tostring(tree, pretty_print=True))

def css_select(tree, css_selector):
    return CSSSelector(css_selector)(tree)