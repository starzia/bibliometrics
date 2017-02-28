from professor_scraper import scrape_professors
from web_util import Selector, HrefSelector, HrefListSelector


def scrape_dartmouth():
    return scrape_professors(school_name='Dartmouth',
                             directory_url='http://www.tuck.dartmouth.edu/faculty/faculty-directory',
                             extracts_faculty_urls=HrefListSelector('div.facultyGrid a'),
                             extracts_title=Selector('div.title h3'),
                             extracts_name=Selector('div.title h2'),
                             extracts_cv_url=None,
                             extracts_personal_url=HrefSelector('div.title a', 'http'),
                             extracts_gscholar_url=None)

if __name__ == '__main__':
    profs = scrape_dartmouth()