from professor_scraper import scrape_professors, Selector, HrefSelector
from web_util import css_select


def scrape_dartmouth():
    return scrape_professors(school_name='Dartmouth',
                             directory_url='http://www.tuck.dartmouth.edu/faculty/faculty-directory',
                             extracts_faculty_urls=\
                                 lambda tree: ['http://www.tuck.dartmouth.edu' + a.get('href').strip()
                                               for a in css_select(tree, 'div.facultyGrid a')],
                             extracts_title=Selector('div.title h3'),
                             extracts_name=Selector('div.title h2'),
                             extracts_cv_url=None,
                             extracts_personal_url=HrefSelector('div.title a', 'http'),
                             extracts_gscholar_url=None)

if __name__ == '__main__':
    profs = scrape_dartmouth()