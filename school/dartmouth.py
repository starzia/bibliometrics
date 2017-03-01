from professor_scraper import scrape_professors
from web_util import Selector, HrefSelector, HrefListSelector, css_select, strip_whitespace, get_tree


get_personal_url = HrefSelector('div.title a', 'http')


def get_papers(url, tree):
    # first try the "personal page" for the faculty,
    #   eg http://faculty.tuck.dartmouth.edu/ron-adner/curriculum-vitae/
    personal_url = get_personal_url(url, tree)
    if personal_url is not None:
        cv_url = personal_url + 'curriculum-vitae/'
        p_tree = get_tree(cv_url)
        if p_tree is not None:
            # find the bulleted list for publications
            for heading in css_select(p_tree, 'h3'):
                if 'publications' in heading.text.lower():
                    # look for the first <UL> under the publications header
                    next = heading
                    while next is not None:
                        if next.name == 'ul':
                            return cv_url, [strip_whitespace(li.text) for li in css_select(next, 'li')]
                        next = next.next_element

    # if we failed, then get the selected publications from the faculty directory,
    #   eg: http://www.tuck.dartmouth.edu/faculty/faculty-directory/ron-adner
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
                             extracts_personal_url=get_personal_url,
                             extracts_gscholar_url=None,
                             extracts_papers=get_papers)

if __name__ == '__main__':
    profs = scrape_dartmouth()