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
                             extracts_faculty_urls_from_tree=\
      lambda tree: ['http://mitsloan.mit.edu' + a.get('href').strip() for a in css_select(tree, 'div.person-result a')],
                             extracts_title_from_tree=get_title,
                             extracts_name_from_tree=Selector('div.innerwrapper h3:nth-of-type(1)'),
                             extracts_cv_url_from_tree=None,
                             extracts_personal_url_from_tree=HrefSelector('aside.faculty-side a', 'Personal Website'),
                             extracts_google_scholar_url_from_tree=HrefSelector('aside.faculty-side a', 'Google Scholar'))

if __name__ == '__main__':
    profs = scrape_mit()