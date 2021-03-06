#!/usr/bin/python
"""
the main script
"""

import csv_professor_sheet
import os
import pprint
import subprocess
from google_scholar import GoogleScholar, get_year
from professor import *
from professor_scraper import save_paper_list
from web_util import get_bytes

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

from csv_professor_sheet import SpreadSheet

pp = pprint.PrettyPrinter(indent=4)
CV_PATH = 'output/CVs'


def download_cv(prof):
    if prof.cv_url is None:
        return
    time.sleep(1)
    print("downloading CV for " + prof.slug())

    global CV_PATH
    if not os.path.exists(CV_PATH):
        os.makedirs(CV_PATH)

    b = get_bytes(prof.cv_url)
    with open(CV_PATH + '/' + prof.slug() + ".pdf", 'wb') as f:
        f.write(b)


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
    """ :return: a dictionary mapping name sluspreadsheet to cv strinspreadsheet"""
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


def get_missing_google_scholar_pages(spreadsheet, school=None):
    profs = spreadsheet.read_profs()
    random.shuffle(profs)
    with GoogleScholar() as scholar:
        for p in profs:
            if school is not None and p.school != school:
                continue
            if p.google_scholar_url is None:
                print(p.name)
                p.google_scholar_url = scholar.find_google_scholar_page(p)
                spreadsheet.save_prof(p)


def download_scholar_profiles(spreadsheet, school=None):
    professors = spreadsheet.read_profs()
    with GoogleScholar() as scholar:
        for p in professors:
            if school and p.school != school:
                continue
            if p.google_scholar_url:
                print(p.slug())
                save_paper_list('scholar_profile', p, scholar.scrape_profile(p.google_scholar_url))


def download_scholar_search_results(spreadsheet, school=None):
    professors = spreadsheet.read_profs()
    with GoogleScholar() as scholar:
        for p in professors:
            if school and p.school != school:
                continue
            print(p.slug())
            if not p.google_scholar_url:
                save_paper_list('scholar_search', p, scholar.scrape_search_results(p))


def ask_for_graduation_years(spreadsheet, profs):
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
                spreadsheet.save_prof(p)


def load_mturk_results(csv_filename):
    observed_answers = {}
    with open(csv_filename, 'r') as csvfile:
        for row in csv_professor_sheet.reader(csvfile, delimiter=',', quotechar='"'):
            name_slug = row[3].split('/')[-1].split('.')[0]
            phd_year = get_year(row[6])
            if not phd_year:
                phd_year = get_year(row[5])
            if not phd_year:
                continue
            if name_slug not in observed_answers:
                observed_answers[name_slug] = []
            observed_answers[name_slug].append(phd_year)
    # majority vote
    year_to_record = {}
    for slug, answers in observed_answers.items():
        # if an answer is in the majority, record it
        for a in answers:
            if answers.count(a) > len(answers) * 0.5:
                year_to_record[slug] = a
                continue
    # save results
    ss = SpreadSheet()
    profs = ss.read_profs()
    for p in profs:
        if p.slug() in year_to_record and year_to_record[p.slug()] != p.graduation_year:
            p.graduation_year = year_to_record[p.slug()]
            time.sleep(1)
            print("%s: saving graduation year %s" % (p.slug(), p.graduation_year))
            spreadsheet.save_prof(p)


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


def rescrape(spreadsheet, school_scraper):
    profs = spreadsheet.read_profs()
    new_profs = school_scraper()
    for p in new_profs:
        for p2 in profs:
            if p2.slug() == p.slug():
                print("merging new data for " + p.slug())
                p.merge(p2)
    spreadsheet.update_profs(new_profs)


if __name__ == '__main__':
    spreadsheet = SpreadSheet()
    do_reload = False
    if do_reload:
        profs = scrape_all_schools()
        get_missing_google_scholar_pages(spreadsheet)
        for p in profs:
            # look for CV and Scholar links on any personal website
            p.parse_personal_website()
            download_cv(p)
        convert_CVs_to_text()
        spreadsheet.append_profs(profs)
        get_missing_google_scholar_pages(spreadsheet)
        download_scholar_profiles(spreadsheet)
        download_scholar_search_results(spreadsheet)
    profs = spreadsheet.read_profs()
    all_CVs = load_CVs()
    print("Total of %d professors found" % len(profs))