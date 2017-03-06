import os
from professor import Professor
from web_util import get_tree, strip_whitespace
from time import sleep
from typing import Callable, List, Optional, AnyStr
from bs4 import Tag


def is_job_title(candidate):
    lowercase = candidate.lower()
    return "professor" in lowercase or "lecturer" in lowercase


def title_is_tenure_track(title):
    lowercase = title.lower()
    return "professor" in lowercase and "adjunct" not in lowercase \
                and "emeritus" not in lowercase and 'emerita' not in lowercase \
                and "clinical" not in lowercase and "visiting" not in lowercase \
                and "research assistant" not in lowercase


def scrape_professors(school_name: str,
                      directory_url: str,
                      extracts_faculty_urls: Callable[[str, Tag], List[str]],
                      extracts_title: Callable[[Tag], str],
                      extracts_name: Callable[[Tag], str],
                      extracts_cv_url: Optional[Callable[[str, Tag], str]] = None,
                      extracts_personal_url: Optional[Callable[[str, Tag], str]] = None,
                      extracts_gscholar_url: Optional[Callable[[str, Tag], str]] = None,
                      extracts_papers: Optional[Callable[[str, Tag], List[str]]] = None) -> List[Professor]:
    """ As a side-effect, this function also writes the lists of publications to disk."""
    profs = []
    # get the faculty index page
    tree = get_tree(directory_url)
    for faculty_url in extracts_faculty_urls(directory_url, tree):
        sleep(2)
        print("scraping " + faculty_url)
        p = scrape_professor(school_name, faculty_url,
                             extracts_title, extracts_name, extracts_cv_url,
                             extracts_personal_url, extracts_gscholar_url, extracts_papers)
        if p is not None:
            print(p)
            profs.append(p)
    return profs


def scrape_professor(school_name,
                     faculty_url,
                     extracts_title,
                     extracts_name,
                     extracts_cv_url = None,
                     extracts_personal_url = None,
                     extracts_gscholar_url = None,
                     extracts_papers = None):
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
    prof = Professor(name=name, title=job_title, cv_url=cv_link, school=school_name,
                     faculty_directory_url=faculty_url, personal_url=personal_url, google_scholar_url=google_scholar_url)
    if extracts_papers is not None:
        paper_list_url, papers = extracts_papers(faculty_url, tree)
        # save paper list to disk
        if paper_list_url and papers and len(papers) > 0:
            prof.paper_list_url = paper_list_url
            save_paper_list('paper_list', prof, papers)
    return prof


def save_paper_list(folder, prof, paper_list):
    path = 'output/' + folder
    if not os.path.exists(path):
        os.makedirs(path)

    with open(path + '/' + prof.slug() + ".txt", 'w') as f:
        for paper in paper_list:
            f.write(str(paper) + '\n')


def load_paper_list(folder, prof) -> List[AnyStr]:
    path = 'output/' + folder
    try:
        with open(path + '/' + prof.slug() + ".txt", 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        return []