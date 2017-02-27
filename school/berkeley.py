from professor_scraper import scrape_professors, Selector, HrefSelector, HrefListSelector, strip_whitespace
from web_util import css_select

def get_title(tree):
    td = css_select(tree, 'td p')[0]
    text_nodes = td.xpath('text()')
    for line in text_nodes:
        line = strip_whitespace(line)
        if len(line) > 0:
            return line


# eg., http://facultybio.haas.berkeley.edu/faculty-list/augenblick-ned/
def scrape_berkeley():
    return scrape_professors(school_name='Berkeley',
                             directory_url='http://facultybio.haas.berkeley.edu/faculty-photo/',
                             extracts_faculty_urls=HrefListSelector('div.faculty-block p a[href]'),
                             extracts_title=get_title,
                             extracts_name=Selector('td p span strong'),
                             extracts_cv_url=HrefSelector('td p a', 'Curriculum Vitae'),
                             extracts_personal_url=HrefSelector('td p a', 'http'),
                             extracts_gscholar_url=None)

if __name__ == '__main__':
    profs = scrape_berkeley()