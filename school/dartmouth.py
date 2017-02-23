from professor_scraper import scrape_professors, Selector, HrefSelector
from web_util import css_select


def scrape_dartmouth():
    return scrape_professors(school_name='Dartmouth',
                             directory_url='http://www.tuck.dartmouth.edu/faculty/faculty-directory',
                             extracts_faculty_urls_from_tree=\
                                 lambda tree: ['http://www.tuck.dartmouth.edu' + a.get('href').strip()
                                               for a in css_select(tree, 'div.facultyGrid a')],
                             extracts_title_from_tree=Selector('div.title h3'),
                             extracts_name_from_tree=Selector('div.title h2'),
                             extracts_cv_url_from_tree=None,
                             extracts_personal_url_from_tree=HrefSelector('div.title a', 'http'),
                             extracts_google_scholar_url_from_tree=None)

if __name__ == '__main__':
    profs = scrape_dartmouth()