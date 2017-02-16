#!/usr/bin/python
'''
To prepare, run:
pip install lxml cssselect requests pprint

Then just run this without any paramenters.
'''

import lxml.html
from lxml.cssselect import CSSSelector
import requests
import pprint

pp = pprint.PrettyPrinter(indent=4)

def scrape_all():
    profs = []
    profs.append(scrape_kellogg())
    pp.pprint(profs)

def get_tree(url):
    r = requests.get(url)
    return lxml.html.fromstring(r.text)

def scrape_kellogg():
    """
    :return: a list of faculty objects for the Kellogg School of Management
    """
    faculty = []
    # get the faculty index page
    tree = get_tree('http://www.kellogg.northwestern.edu/faculty/advanced_search.aspx')
    # look for the faculty options listed in a select element
    sel = CSSSelector('select#plcprimarymaincontent_1_selBrowseByName option')
    for option in sel(tree):
        if (option.get('value') != ''):
            print option.get('value') + ": " + option.text
            netId = option.get('value')
            f = scrape_kellogg_faculty(netId)
            if f is not None:
                faculty.append(f)

def scrape_kellogg_faculty(netId):
    """ :return: a faculty object or None if it's not a tenure track faculty """
    tree = get_tree('http://www.kellogg.northwestern.edu/Faculty/Faculty_Search_Results.aspx?netid=' + netId)
    job_title = CSSSelector('span#lblTitle')(tree)[0].text
    if not title_is_tenure_track(job_title):
        return None
    name = CSSSelector('span#lblName')(tree)[0].text
    cv_link = None
    for a in CSSSelector('div#sideNav3 a')(tree):
        if "Download Vita (pdf)" in a.text:
            cv_link = a.get('href')
    return {'name':name, 'title':job_title, 'cv_link': cv_link}

def title_is_tenure_track(title):
    lowercase = title.lower()
    return "professor" in lowercase and "adjunct" not in lowercase and "emeritus" not in lowercase \
                and "clinical" not in lowercase and "visiting" not in lowercase

if __name__ == '__main__':
    scrape_all();