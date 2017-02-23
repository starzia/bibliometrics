from professor import Professor
from web_util import get_tree, css_select
from time import sleep
import re


def title_is_tenure_track(title):
    lowercase = title.lower()
    return "professor" in lowercase and "adjunct" not in lowercase and "emeritus" not in lowercase \
                and "clinical" not in lowercase and "visiting" not in lowercase \
                and "research assistant" not in lowercase


def strip_whitespace(str):
    if str is None:
        return None
    return re.sub(r"\s+", ' ', str).strip()


class Selector:
    def __init__(self, css_selector):
        self.css_selector = css_selector

    def __call__(self, tree):
        try:
            return strip_whitespace(css_select(tree, self.css_selector)[0].text)
        except AttributeError:
            return None


class HrefSelector:
    def __init__(self, css_selector, anchor_text):
        self.css_selector = css_selector
        self.anchor_text = anchor_text

    def __call__(self, tree):
        for a in css_select(tree, self.css_selector):
            if self.anchor_text in a.text:
                return a.get('href')


def scrape_professors(school_name, directory_url,
                      extracts_faculty_urls_from_tree,
                      extracts_title_from_tree,
                      extracts_name_from_tree,
                      extracts_cv_url_from_tree=None,
                      extracts_personal_url_from_tree=None,
                      extracts_google_scholar_url_from_tree=None):
    """ :return: a list of Professor objects """
    profs = []
    # get the faculty index page
    tree = get_tree(directory_url)
    for faculty_url in extracts_faculty_urls_from_tree(tree):
        sleep(2)
        print "scraping " + faculty_url
        p = scrape_professor(school_name, faculty_url,
                             extracts_title_from_tree, extracts_name_from_tree, extracts_cv_url_from_tree,
                             extracts_personal_url_from_tree, extracts_google_scholar_url_from_tree)
        if p is not None:
            print p
            profs.append(p)
    return profs


def scrape_professor(school_name,
                     faculty_url,
                     extracts_title_from_tree,
                     extracts_name_from_tree,
                     extracts_cv_url_from_tree,
                     extracts_personal_url_from_tree,
                     extracts_google_scholar_url_from_tree):
    """ :return: a Professor object or None if it's not a tenure track faculty """
    tree = get_tree(faculty_url)
    job_title = strip_whitespace(extracts_title_from_tree(tree))
    if job_title is None:
        print "WARNING: job title not found on "+faculty_url
        return None
    if not title_is_tenure_track(job_title):
        return None
    name = extracts_name_from_tree(tree)
    cv_link = None if extracts_cv_url_from_tree is None else extracts_cv_url_from_tree(tree)
    personal_url = None if extracts_personal_url_from_tree is None else extracts_personal_url_from_tree(tree)
    google_scholar_url = None if extracts_google_scholar_url_from_tree is None else extracts_google_scholar_url_from_tree(tree)
    return Professor(name=name, title=job_title, cv_url=cv_link, school=school_name,
                     faculty_directory_url=faculty_url, personal_url=personal_url, google_scholar_url=google_scholar_url)