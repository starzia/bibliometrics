#!/usr/bin/python
'''
This is written in Python 3

To prepare, run:
pip install lxml cssselect requests pprint

Then just run this without any paramenters.
'''

import lxml.html
from lxml.cssselect import CSSSelector
import requests
import pprint
import pickle
import os

pp = pprint.PrettyPrinter(indent=4)

def lower_alpha(str):
    """ :return: a transformation of the string including only lowercase letters and underscore"""
    return ''.join(char for char in str.lower().replace(' ', '_') if char.isalnum() or char is '_')

class Professor:
    def __init__(self, school, name, title, cv_url=None, graduation_year=None, staff_id=None):
        self.school = school
        self.name = name
        self.title = title
        self.cv_url = cv_url
        self.graduation_year = graduation_year
        self.staff_id = staff_id

    def slug(self):
        """ :return: a human-readable string identifying the professor, to be used to filenames and such. """
        return lower_alpha(self.school + '_' + self.name)

    def download_cv(self):
        print "downloading CV for " + self.slug()
        if self.cv_url is None:
            print "WARNING: missing CV!"
            return

        cv_path = 'CVs'
        if not os.path.exists(cv_path):
            os.makedirs(cv_path)

        r = requests.get(self.cv_url)
        with open(cv_path + '/' + self.slug() + ".pdf", 'wb') as f:
            f.write(r.content)

def scrape_all_schools():
    profs = []
    profs.extend(scrape_kellogg())
    pp.pprint(profs)

    # save professor info to disk
    output = open('professors.pkl', 'wb')
    pickle.dump(profs, output)
    output.close()

    return profs

def scrape_CVs(profs):
    # download CVs
    for prof in profs:
        prof.download_cv()

def get_tree(url):
    r = requests.get(url)
    return lxml.html.fromstring(r.text)

def css_select(tree, css_selector):
    return CSSSelector(css_selector)(tree)

def scrape_kellogg():
    """
    :return: a list of faculty objects for the Kellogg School of Management
    """
    faculty = []
    # get the faculty index page
    tree = get_tree('http://www.kellogg.northwestern.edu/faculty/advanced_search.aspx')
    # look for the faculty options listed in a select element
    for option in css_select(tree, 'select#plcprimarymaincontent_1_selBrowseByName option'):
        if (option.get('value') != ''):
            print option.get('value') + ": " + option.text
            netId = option.get('value')
            f = scrape_kellogg_faculty(netId)
            if f is not None:
                faculty.append(f)
    return faculty

def scrape_kellogg_faculty(netId):
    """ :return: a faculty object or None if it's not a tenure track faculty """
    tree = get_tree('http://www.kellogg.northwestern.edu/Faculty/Faculty_Search_Results.aspx?netid=' + netId)
    job_title = css_select(tree, 'span#lblTitle')[0].text
    if not title_is_tenure_track(job_title):
        return None
    name = css_select(tree, 'span#lblName')[0].text
    cv_link = None
    for a in css_select(tree, 'div#sideNav3 a'):
        if "Download Vita (pdf)" in a.text:
            cv_link = a.get('href')
    return Professor(name=name, title=job_title, cv_url=cv_link, school='Kellogg', staff_id=netId)

def title_is_tenure_track(title):
    lowercase = title.lower()
    return "professor" in lowercase and "adjunct" not in lowercase and "emeritus" not in lowercase \
                and "clinical" not in lowercase and "visiting" not in lowercase \
                and "research assistant" not in lowercase

def load_profs_from_file():
    with open('professors.pkl', 'r') as input:
        return pickle.load(input)

if __name__ == '__main__':
    do_reload = True
    if do_reload:
        profs = scrape_all_schools()
    else:
        profs = load_profs_from_file()
    scrape_CVs(profs)