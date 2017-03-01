from professor_scraper import scrape_professors
from web_util import css_select, Selector, HrefSelector, HrefListSelector, strip_whitespace
from bs4 import NavigableString


def get_title(tag):
    for e in css_select(tag, 'td p')[0].children:
        if isinstance(e, NavigableString):
            e = strip_whitespace(e)
            if len(e) > 0:
                return e


def get_papers(url, tree):
    papers = []
    # find the bulleted list for publications
    for heading in css_select(tree, '#center-col strong'):
        if 'Publications' in heading.text:
            # look for the first <UL> under the publications header
            next = heading
            while next is not None:
                if next.name == 'ul':
                    papers = [strip_whitespace(li.text.replace(' PDF.', '')) for li in css_select(next, 'li')]
                    break
                next = next.next_element
    return url, papers


# eg., http://facultybio.haas.berkeley.edu/faculty-list/augenblick-ned/
def scrape_berkeley():
    return scrape_professors(school_name='Berkeley',
                             directory_url='http://facultybio.haas.berkeley.edu/faculty-photo/',
                             extracts_faculty_urls=HrefListSelector('div.faculty-block p a[href]'),
                             extracts_title=get_title,
                             extracts_name=Selector('td p span strong'),
                             extracts_cv_url=HrefSelector('td p a', 'Curriculum Vitae'),
                             extracts_personal_url=HrefSelector('td p a', 'http'),
                             extracts_gscholar_url=None,
                             extracts_papers=get_papers)

if __name__ == '__main__':
    profs = scrape_berkeley()