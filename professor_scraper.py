from professor import Professor
from web_util import get_tree, css_select
from time import sleep
import re
import urllib.parse

def title_is_tenure_track(title):
    lowercase = title.lower()
    return "professor" in lowercase and "adjunct" not in lowercase \
                and "emeritus" not in lowercase and 'emerita' not in lowercase \
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
        except (IndexError, AttributeError):
            return None


class HrefSelector:
    def __init__(self, css_selector, anchor_text):
        self.css_selector = css_selector
        self.anchor_text = anchor_text

    def __call__(self, current_url, tree):
        for a in css_select(tree, self.css_selector):
            if self.anchor_text in a.text:
                return urllib.parse.urljoin(current_url, a.get('href'))


class ListSelector:
    def __init__(self, css_selector):
        self.css_selector = css_selector

    def __call__(self, tree):
        try:
            return [strip_whitespace(e.text) for e in css_select(tree, self.css_selector)]
        except (IndexError, AttributeError):
            return None


class HrefListSelector:
    def __init__(self, css_selector):
        self.css_selector = css_selector

    def __call__(self, current_url, tree):
        try:
            return [urllib.parse.urljoin(current_url, e.get('href').strip())
                    for e in css_select(tree, self.css_selector)]
        except (IndexError, AttributeError):
            return None


def scrape_professors(school_name, directory_url,
                      extracts_faculty_urls,
                      extracts_title,
                      extracts_name,
                      extracts_cv_url=None,
                      extracts_personal_url=None,
                      extracts_gscholar_url=None):
    """ :return: a list of Professor objects """
    profs = []
    # get the faculty index page
    tree = get_tree(directory_url)
    for faculty_url in extracts_faculty_urls(directory_url, tree):
        sleep(2)
        print("scraping " + faculty_url)
        p = scrape_professor(school_name, faculty_url,
                             extracts_title, extracts_name, extracts_cv_url,
                             extracts_personal_url, extracts_gscholar_url)
        if p is not None:
            print(p)
            profs.append(p)
    return profs


def scrape_professor(school_name,
                     faculty_url,
                     extracts_title,
                     extracts_name,
                     extracts_cv_url,
                     extracts_personal_url,
                     extracts_gscholar_url):
    """ :return: a Professor object or None if it's not a tenure track faculty """
    tree = get_tree(faculty_url)
    if tree is None:
        return None
    job_title = strip_whitespace(extracts_title(tree))
    if job_title is None:
        print("WARNING: job title not found on "+faculty_url)
        return None
    if not title_is_tenure_track(job_title):
        return None
    name = extracts_name(tree)
    cv_link = None if extracts_cv_url is None else extracts_cv_url(faculty_url, tree)
    personal_url = None if extracts_personal_url is None else extracts_personal_url(faculty_url, tree)
    google_scholar_url = None if extracts_gscholar_url is None else extracts_gscholar_url(faculty_url, tree)
    return Professor(name=name, title=job_title, cv_url=cv_link, school=school_name,
                     faculty_directory_url=faculty_url, personal_url=personal_url, google_scholar_url=google_scholar_url)