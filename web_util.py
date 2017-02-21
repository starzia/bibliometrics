import lxml.html
from lxml.cssselect import CSSSelector
import requests

import time
import random

def wait():
    time.sleep(3 + random.uniform(0,3))

http_session = requests.Session()

def get_tree(url):
    r = http_session.get(url, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"})
    if r.status_code != 200:
        print "WARNING got %d status code for %s" % (r.status_code, url)
    return lxml.html.fromstring(r.text)

def print_tree(tree):
    print lxml.etree.tostring(tree, pretty_print=True)

def css_select(tree, css_selector):
    return CSSSelector(css_selector)(tree)