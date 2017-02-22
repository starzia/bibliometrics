from professor_scraper import scrape_professors
from web_util import css_select

def scrape_harvard():
    return scrape_professors(school_name="Harvard",
                             directory_url='http://www.hbs.edu/faculty/Pages/browse.aspx',
                             extracts_faculty_urls_from_tree=\
    lambda tree: ['http://www.hbs.edu' + a.get('href').strip() for a in css_select(tree, 'div.faculty-item a')],
                             job_title_selector='p.faculty-title:first-of-type',
                             name_selector='h1.author:first-of-type',
                             extracts_cv_url_from_tree=None)

if __name__ == '__main__':
    profs = scrape_harvard()