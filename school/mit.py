from professor_scraper import scrape_professors, strip_whitespace, title_is_tenure_track, Selector, HrefSelector
from web_util import css_select


def get_title(tree):
    for candidate in [strip_whitespace(c.text) for c in
                      css_select(tree, 'ul#ctl00_content_titles li i') + css_select(tree, 'ul#ctl00_content_areas li')]:
        if candidate is not None and title_is_tenure_track(candidate):
            return candidate
    return None


def scrape_mit():
    return scrape_professors(school_name="MIT",
                             directory_url='http://mitsloan.mit.edu/faculty-and-research/faculty-directory/',
                             extracts_faculty_urls=\
      lambda tree: ['http://mitsloan.mit.edu' + a.get('href').strip() for a in css_select(tree, 'div.person-result a')],
                             extracts_title=get_title,
                             extracts_name=Selector('div.innerwrapper h3:nth-of-type(1)'),
                             extracts_cv_url=None,
                             extracts_personal_url=HrefSelector('aside.faculty-side a', 'Personal Website'),
                             extracts_gscholar_url=HrefSelector('aside.faculty-side a', 'Google Scholar'))

if __name__ == '__main__':
    profs = scrape_mit()