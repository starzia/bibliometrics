from professor_scraper import scrape_professors
from web_util import css_select

def get_cv_url(tree):
    for a in css_select(tree, 'div.faculty-navigation div.links a'):
        if "Curriculum Vitae" in a.text:
            return 'http://www.hbs.edu' + a.get('href').replace(' ', '%20')
    return None

def get_personal_url(tree):
    for a in css_select(tree, 'div.faculty-navigation div.links a'):
        if "Personal Website" in a.text:
            return a.get('href')
    return None

def scrape_harvard():
    return scrape_professors(school_name="Harvard",
                             directory_url='http://www.hbs.edu/faculty/Pages/browse.aspx',
                             extracts_faculty_urls_from_tree=\
      lambda tree: ['http://www.hbs.edu' + a.get('href').strip() for a in css_select(tree, 'div.faculty-item a')],
                             job_title_selector='p.faculty-title:first-of-type',
                             name_selector='h1.author:first-of-type',
                             extracts_cv_url_from_tree=get_cv_url,
                             extracts_personal_url_from_tree=get_personal_url)

if __name__ == '__main__':
    profs = scrape_harvard()