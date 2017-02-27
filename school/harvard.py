from professor_scraper import scrape_professors, Selector, HrefSelector, HrefListSelector
from web_util import css_select


def get_personal_url(tree):
    for a in css_select(tree, 'div.faculty-navigation div.links a'):
        if "Personal Website" in a.text or "Home Page" in a.text:
            return a.get('href')
    return None


def scrape_harvard():
    return scrape_professors(school_name="Harvard",
                             directory_url='http://www.hbs.edu/faculty/Pages/browse.aspx',
                             extracts_faculty_urls=HrefListSelector('div.faculty-item a'),
                             extracts_title=Selector('p.faculty-title:nth-of-type(1)'),
                             extracts_name=Selector('h1.author:nth-of-type(1)'),
                             extracts_cv_url=HrefSelector('div.faculty-navigation div.links a', 'Curriculum Vitae'),
                             extracts_personal_url=get_personal_url)

if __name__ == '__main__':
    profs = scrape_harvard()