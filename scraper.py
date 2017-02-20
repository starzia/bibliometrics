#!/usr/bin/python
'''
This is written in Python 3

To prepare, run:
pip install lxml cssselect requests pprint
# pdfminer installs the pdf2txt.py command joblib
pip install pdfminer

Then just run ./scraper.py without any paramenters.
'''

import lxml.html
from lxml.cssselect import CSSSelector
import requests
import pprint
import pickle
import os
import subprocess
import urllib
import time
import random

pp = pprint.PrettyPrinter(indent=4)
CV_PATH = 'CVs'

def lower_alpha(str):
    """ :return: a transformation of the string including only lowercase letters and underscore"""
    return ''.join(char for char in str.lower().replace(' ', '_') if char.isalnum() or char is '_')

def wait():
    time.sleep(3 + random.uniform(0,3))

class Professor:
    def __init__(self, school, name, title, cv_url=None, graduation_year=None, staff_id=None, google_scholar_url=None):
        self.school = school
        self.name = name
        self.title = title
        self.cv_url = cv_url
        self.graduation_year = graduation_year
        self.staff_id = staff_id
        self.google_scholar_url = google_scholar_url

    def slug(self):
        """ :return: a human-readable string identifying the professor, to be used to filenames and such. """
        return lower_alpha(self.school + '_' + self.name)

    def download_cv(self):
        wait()
        print "downloading CV for " + self.slug()
        if self.cv_url is None:
            print "WARNING: missing CV!"
            return

        global CV_PATH
        if not os.path.exists(CV_PATH):
            os.makedirs(CV_PATH)

        r = requests.get(self.cv_url)
        with open(CV_PATH + '/' + self.slug() + ".pdf", 'wb') as f:
            f.write(r.content)

    def find_google_scholar_page(self):
        """NOTE: google is very proactive about blocking requests if it thinks you are a bot,
        so this sometimes results in a 503 error. """
        wait()
        # get search results page
        tree = get_tree('https://scholar.google.com/scholar?q=author%%3A"%s"+%s' %
                        (urllib.quote_plus(self.name), self.school))
        anchors = css_select(tree, 'h4.gs_rt2 a')
        if len(anchors) > 0:
            if len(anchors) > 1:
                print "WARNING: multiple author pages found for %s" % self.name
            self.google_scholar_url = anchors[0].get('href')

def scrape_all_schools():
    """as a side-effect this saves a pickled version of the returned list of professors"""
    profs = []
    profs.extend(scrape_kellogg())
    pp.pprint(profs)
    save(profs)
    return profs

def save(profs):
    # save professor info to disk
    output = open('professors.pkl', 'wb')
    pickle.dump(profs, output)
    output.close()

def convert_CVs_to_text():
    for file_path in os.listdir(CV_PATH):
        if file_path.endswith(".pdf"):
            slug = file_path.replace('.pdf','')
            print 'reading ' + file_path
            # The commandline version of pdf2txt actually works better than the Python slate package.
            # Slate drops a lot of whitespace and newlines.
            cv = subprocess.check_output(['pdf2txt.py', CV_PATH + '/' + file_path])
            with open(CV_PATH + '/' + slug + '.txt', 'w') as f:
                f.write(cv)

def load_CVs():
    """ :return: a dictionary mapping name slugs to cv strings"""
    all_CVs = {}
    for file_path in os.listdir(CV_PATH):
        if file_path.endswith(".txt"):
            slug = file_path.replace('.txt','')
            with open(CV_PATH + '/' + file_path, 'r') as f:
                all_CVs[slug] = f.read()
    return all_CVs

http_session = requests.Session()

def get_tree(url):
    r = http_session.get(url, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"})
    if r.status_code != 200:
        print "WARNING got %d status code for %s" % (r.status_code, url)
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

def show_editorial_service(all_CVs):
    for name, cv in all_CVs.iteritems():
        print
        print name
        for line in cv.lower().splitlines():
            if ("editor" in line):
                print line

if __name__ == '__main__':
    do_reload = False
    if do_reload:
        profs = scrape_all_schools()
        for p in profs:
            p.download_cv()
            p.get_google_scholar_page()
        convert_CVs_to_text()
    profs = load_profs_from_file()
    all_CVs = load_CVs()
    show_editorial_service(all_CVs)
    save(profs)

    # TODO: remove the code below
    for p in profs:
        print p.name
        p.find_google_scholar_page()
    save(profs)