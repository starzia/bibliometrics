from professor_scraper import scrape_professors, Selector, HrefSelector, strip_whitespace
from web_util import css_select
import lxml
import string
from selenium import webdriver

def get_faculty_urls(tree):
    """Yale's webserver doesn't return the real faculty list unless we use a real, javascript-enabled browser."""
    urls = []
    selenium = webdriver.Firefox()
    selenium.get('http://som.yale.edu/faculty-research/faculty-directory')
    for a in selenium.find_elements_by_css_selector('h4.faculty--teaser-name a'):
        urls.append(a.get_attribute('href'))
    selenium.quit()
    return urls


def scrape_yale():
    return scrape_professors(school_name='Yale',
                             directory_url='http://som.yale.edu/faculty-research/faculty-directory',
                             extracts_faculty_urls_from_tree=get_faculty_urls,
                             extracts_title_from_tree=Selector('h1.title'),
                             extracts_name_from_tree=Selector('h2.sub-title'),
                             # for CV and GS, see: http://som.yale.edu/victoria-l-brescoll
                             extracts_cv_url_from_tree=HrefSelector('ul.faculty--info-list li.url a', 'CV'),
                             # for website, see: http://som.yale.edu/nicholas-c-barberis
                             extracts_personal_url_from_tree=HrefSelector('ul.faculty--info-list li.url a', 'Website'),
                             extracts_google_scholar_url_from_tree=HrefSelector('ul.faculty--info-list li.url a', 'Google Scholar'))

if __name__ == '__main__':
    profs = scrape_yale()
