from professor_scraper import scrape_professors, is_job_title
from web_util import css_select, strip_whitespace, Selector, HrefSelector, HrefListSelector


def get_title(tree):
    # We don't know exactly where the title will be so we keep looking until we find one that matches.
    for candidate in [strip_whitespace(c.text) for c in
                      css_select(tree, 'ul#ctl00_content_titles li i') + css_select(tree, 'ul#ctl00_content_areas li')]:
        if candidate is not None and is_job_title(candidate):
            return candidate
    return None


def scrape_mit():
    return scrape_professors(school_name="MIT",
                             directory_url='http://mitsloan.mit.edu/faculty-and-research/faculty-directory/',
                             extracts_faculty_urls=HrefListSelector('div.person-result a'),
                             extracts_title=get_title,
                             extracts_name=Selector('div.innerwrapper h3:nth-of-type(1)'),
                             extracts_cv_url=None,
                             extracts_personal_url=HrefSelector('aside.faculty-side a', 'Personal Website'),
                             extracts_gscholar_url=HrefSelector('aside.faculty-side a', 'Google Scholar'))

if __name__ == '__main__':
    profs = scrape_mit()