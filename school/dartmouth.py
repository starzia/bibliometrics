from professor_scraper import scrape_professors
from web_util import Selector, HrefSelector, HrefListSelector, css_select, strip_whitespace


def get_papers(url, tree):
    # find the bulleted list for publications
    for heading in css_select(tree, 'h3'):
        if 'Publications' in heading.text:
            # look for the first <UL> under the publications header
            next = heading
            while next is not None:
                if next.name == 'ul':
                    return url, [strip_whitespace(li.text) for li in css_select(next, 'li')]
                    break
                next = next.next_element
    return None, None


def scrape_dartmouth():
    return scrape_professors(school_name='Dartmouth',
                             directory_url='http://www.tuck.dartmouth.edu/faculty/faculty-directory',
                             extracts_faculty_urls=HrefListSelector('div.facultyGrid a'),
                             extracts_title=Selector('div.title h3'),
                             extracts_name=Selector('div.title h2'),
                             extracts_cv_url=None,
                             extracts_personal_url=HrefSelector('div.title a', 'http'),
                             extracts_gscholar_url=None,
                             extracts_papers=get_papers)

if __name__ == '__main__':
    profs = scrape_dartmouth()