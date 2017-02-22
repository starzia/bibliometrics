from professor_scraper import scrape_professors
from web_util import css_select

def get_personal_url(tree):
    for a in css_select(tree, 'aside.faculty-side a'):
        if "Personal Website" in a.text:
            return a.get('href')
    return None

def scrape_mit():
    return scrape_professors(school_name="MIT",
                             directory_url='http://mitsloan.mit.edu/faculty-and-research/faculty-directory/',
                             extracts_faculty_urls_from_tree=\
      lambda tree: ['http://mitsloan.mit.edu/' + a.get('href').strip() for a in css_select(tree, 'div.person-result a')],
                             job_title_selector='ul.ctl00_content_titles:first-of-type',
                             name_selector='div.inner-wrapper h3:first-of-type',
                             extracts_cv_url_from_tree=None,
                             extracts_personal_url_from_tree=get_personal_url)

if __name__ == '__main__':
    profs = scrape_mit()