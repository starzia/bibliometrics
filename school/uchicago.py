from professor_scraper import scrape_professors
from web_util import Selector, HrefSelector, HrefListSelector


def scrape_uchicago():
    return scrape_professors(
            school_name="Chicago",
            directory_url='https://www.chicagobooth.edu/faculty/directory',
            extracts_faculty_urls=HrefListSelector('div.faculty-listing-name a'),
            extracts_title=Selector('div.faculty-bio-info h2:nth-of-type(1)'),
            extracts_name=Selector('div.faculty-bio-info h1:nth-of-type(1)'),
            extracts_cv_url=HrefSelector('ul.resource-list a', 'Curriculum Vitae'),
            extracts_personal_url=HrefSelector('p.faculty-link-website a', 'Personal Website'))

if __name__ == '__main__':
    profs = scrape_uchicago()