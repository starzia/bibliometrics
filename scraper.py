#!/usr/bin/python
"""
the main script
"""

import os
import requests
import pprint
import subprocess
import google_scholar
from professor import *
from school.kellogg import scrape_kellogg
from school.harvard import scrape_harvard
from school.uchicago import scrape_uchicago
from school.mit import scrape_mit
from school.stanford import scrape_stanford
from school.upenn import scrape_upenn
from school.berkeley import scrape_berkeley
from school.dartmouth import scrape_dartmouth
from school.yale import scrape_yale
from school.columbia import scrape_columbia


from google_sheets import GoogleSheets
from selenium import webdriver

pp = pprint.PrettyPrinter(indent=4)
CV_PATH = 'output/CVs'


def download_cv(prof):
    wait()
    print("downloading CV for " + prof.slug())
    if prof.cv_url is None:
        print("WARNING: missing CV!")
        return

    global CV_PATH
    if not os.path.exists(CV_PATH):
        os.makedirs(CV_PATH)

    r = requests.get(prof.cv_url)
    with open(CV_PATH + '/' + prof.slug() + ".pdf", 'wb') as f:
        f.write(r.content)


def convert_CVs_to_text():
    for file_path in os.listdir(CV_PATH):
        if file_path.endswith(".pdf"):
            slug = file_path.replace('.pdf','')
            print('reading ' + file_path)
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


def show_editorial_service(all_CVs):
    for name, cv in all_CVs.iteritems():
        print()
        print(name)
        for line in cv.lower().splitlines():
            if "editor" in line:
                print(line)


def get_missing_google_scholar_pages(google_sheets, school=None):
    selenium_driver = webdriver.Firefox()
    profs = google_sheets.read_profs()
    random.shuffle(profs)
    for p in profs:
        if school is not None and p.school != school:
            continue
        if p.google_scholar_url is None:
            print(p.name)
            p.google_scholar_url = google_scholar.find_google_scholar_page(p, selenium_driver)
            google_sheets.save_prof(p)
    selenium_driver.close()


def ask_for_graduation_years(google_sheets, profs):
    for p in profs:
        if p.graduation_year is None:
            # show the CV
            # !!!: this works on Mac only
            subprocess.check_output("curl %s | open -f -a Preview" % p.cv_url, shell=True)
            # ask for the graduation year
            print(p.name)
            school = input("Graduation School? ")
            year_str = input("Graduation Year? ")
            if year_str is not None and len(year_str) > 0:
                p.graduation_year = int(year_str)
                p.graduation_school = school
                google_sheets.save_prof(p)


def scrape_all_schools():
    profs = []
    profs.extend(scrape_kellogg())
    profs.extend(scrape_harvard())
    profs.extend(scrape_uchicago())
    profs.extend(scrape_mit())
    profs.extend(scrape_stanford())
    profs.extend(scrape_upenn())
    profs.extend(scrape_berkeley())
    profs.extend(scrape_dartmouth())
    profs.extend(scrape_yale())
    profs.extend(scrape_columbia())
    return profs


def rescrape(gs, school_scraper):
    profs = gs.read_profs()
    new_profs = school_scraper()
    for p in new_profs:
        for p2 in profs:
            if p2.slug() == p.slug():
                print("merging new data for " + p.slug())
                p.merge(p2)
    gs.update_profs(new_profs)


if __name__ == '__main__':
    gs = GoogleSheets()
    do_reload = False
    if do_reload:
        profs = scrape_all_schools()
        get_missing_google_scholar_pages(gs)
        for p in profs:
            download_cv(p)
            p.parse_personal_website()
        convert_CVs_to_text()
        gs.append_profs(profs)
    profs = gs.read_profs()
    all_CVs = load_CVs()
    print("Total of %d professors found" % len(profs))