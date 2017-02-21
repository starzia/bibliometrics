#!/usr/bin/python
'''
This is written in Python 3

To prepare, run:
pip install lxml cssselect requests pprint
# pdfminer installs the pdf2txt.py command joblib
pip install pdfminer

Then just run ./scraper.py without any paramenters.
'''

import pprint
import subprocess
from professor import *
from google_sheets import GoogleSheets
from selenium import webdriver

pp = pprint.PrettyPrinter(indent=4)
CV_PATH = 'CVs'

def scrape_all_schools():
    """as a side-effect this saves a pickled version of the returned list of professors"""
    profs = []
    profs.extend(scrape_kellogg())
    pp.pprint(profs)
    return profs

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

def show_editorial_service(all_CVs):
    for name, cv in all_CVs.iteritems():
        print
        print name
        for line in cv.lower().splitlines():
            if ("editor" in line):
                print line

if __name__ == '__main__':
    gs = GoogleSheets()
    do_reload = False
    if do_reload:
        profs = scrape_all_schools()
        for p in profs:
            p.download_cv()
            p.get_google_scholar_page()
            gs.save_prof(p)
        convert_CVs_to_text()
    profs = gs.read_profs()
    all_CVs = load_CVs()
    show_editorial_service(all_CVs)
    pp.pprint(profs)
    print "Total of %d professors found" % len(profs)

    # TODO: remove below
    # try to get google scholar pages where they are missing
    selenium_driver = webdriver.Firefox()
    random.shuffle(profs)
    for p in profs:
        if p.google_scholar_url is None:
#    for p in [p for p in profs if p.name == "Brian Uzzi"]:
            p.find_google_scholar_page(selenium_driver)
            gs.save_prof(p)