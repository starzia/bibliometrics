from professor_scraper import scrape_professors
from web_util import Selector, HrefSelector, HrefListSelector


def scrape_harvard():
    return scrape_professors(school_name="Harvard",
                             directory_url='http://www.hbs.edu/faculty/Pages/browse.aspx',
                             extracts_faculty_urls=HrefListSelector('div.faculty-item a'),
                             extracts_title=Selector('p.faculty-title'),
                             extracts_name=Selector('h1.author'),
                             extracts_cv_url=HrefSelector('div.faculty-navigation div.links a', 'Curriculum Vitae'),
                             extracts_personal_url=HrefSelector('div.faculty-navigation div.links a',
                                                                'Personal Website', 'Home Page'))

if __name__ == '__main__':
    profs = scrape_harvard()