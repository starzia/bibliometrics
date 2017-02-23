from professor_scraper import scrape_professors, Selector, HrefSelector, strip_whitespace
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
                             extracts_faculty_urls_from_tree=\
                lambda tree: [a.get('href').strip() for a in css_select(tree, 'div.faculty-block p a[href]')],
                             extracts_title_from_tree=get_title,
                             extracts_name_from_tree=Selector('td p span strong'),
                             extracts_cv_url_from_tree=HrefSelector('td p a', 'Curriculum Vitae'),
                             extracts_personal_url_from_tree=HrefSelector('td p a', 'http'),
                             extracts_google_scholar_url_from_tree=None)

if __name__ == '__main__':
    profs = scrape_berkeley()