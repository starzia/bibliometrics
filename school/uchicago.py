from professor_scraper import scrape_professors
from web_util import css_select

def get_cv_url(tree):
    for a in css_select(tree, 'ul.resource-list a'):
        if "Curriculum Vitae" in a.text:
            return a.get('href')
    return None

def get_personal_url(tree):
    for a in css_select(tree, 'p.faculty-link-website a'):
        if "Personal Website" in a.text:
            return a.get('href')
    return None

def scrape_uchicago():
    return scrape_professors(school_name="Chicago",
                             directory_url='https://www.chicagobooth.edu/faculty/directory',
                             extracts_faculty_urls_from_tree=\
      lambda tree: ['https://www.chicagobooth.edu' + a.get('href').strip() for a in css_select(tree, 'div.faculty-listing-name a')],
                             job_title_selector='div.faculty-bio-info h2:first-of-type',
                             name_selector='div.faculty-bio-info h1:first-of-type',
                             extracts_cv_url_from_tree=get_cv_url,
                             extracts_personal_url_from_tree=get_personal_url)

if __name__ == '__main__':
    profs = scrape_uchicago()