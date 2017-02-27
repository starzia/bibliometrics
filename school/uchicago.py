from professor_scraper import scrape_professors, Selector, HrefSelector
from web_util import css_select


def scrape_uchicago():
    return scrape_professors(
            school_name="Chicago",
            directory_url='https://www.chicagobooth.edu/faculty/directory',
            extracts_faculty_urls_from_tree=\
      lambda tree: ['https://www.chicagobooth.edu' + a.get('href').strip() for a in css_select(tree, 'div.faculty-listing-name a')],
            extracts_title_from_tree=Selector('div.faculty-bio-info h2:nth-of-type(1)'),
            extracts_name_from_tree=Selector('div.faculty-bio-info h1:nth-of-type(1)'),
            extracts_cv_url_from_tree=HrefSelector('ul.resource-list a', 'Curriculum Vitae'),
            extracts_personal_url_from_tree=HrefSelector('p.faculty-link-website a', 'Personal Website'))

if __name__ == '__main__':
    profs = scrape_uchicago()