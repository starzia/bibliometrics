from professor import Professor
from web_util import get_tree, css_select

def title_is_tenure_track(title):
    lowercase = title.lower()
    return "professor" in lowercase and "adjunct" not in lowercase and "emeritus" not in lowercase \
                and "clinical" not in lowercase and "visiting" not in lowercase \
                and "research assistant" not in lowercase

def scrape_professors(school_name, directory_url,
                      extracts_faculty_urls_from_tree,
                      job_title_selector, name_selector,
                      extracts_cv_url_from_tree=None):
    """ :return: a list of Professor objects """
    profs = []
    # get the faculty index page
    tree = get_tree(directory_url)
    for faculty_url in extracts_faculty_urls_from_tree(tree):
        p = scrape_professor(school_name, faculty_url, job_title_selector, name_selector, extracts_cv_url_from_tree)
        if p is not None:
            print p
            profs.append(p)
    return profs

def scrape_professor(school_name, faculty_url, job_title_selector, name_selector, extracts_cv_url_from_tree):
    """ :return: a Professor object or None if it's not a tenure track faculty """
    tree = get_tree(faculty_url)
    try:
        job_title = css_select(tree, job_title_selector)[0].text.strip()
        if not title_is_tenure_track(job_title):
            return None
    except AttributeError:
        print "WARNING: job title not found on "+faculty_url
        return None
    name = css_select(tree, name_selector)[0].text.strip()
    cv_link = None if extracts_cv_url_from_tree is None else extracts_cv_url_from_tree(tree)
    return Professor(name=name, title=job_title, cv_url=cv_link, school=school_name,
                     faculty_directory_url=faculty_url)
