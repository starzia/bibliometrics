from professor_scraper import scrape_professors
from web_util import Selector, HrefSelector, HrefListSelector, css_select, strip_whitespace, wait, get_tree


def get_papers(url, tree):
    # add "&facInfo=pub" to the faculty url to get the url for the publications tab
    pub_list_url = url + "&facInfo=pub"
    wait()
    pub_tree = get_tree(pub_list_url)
    # find the bulleted list for publications
    for heading in css_select(pub_tree, '.tab-content h3'):
        if 'Articles' in heading.text:
            # look for the first <OL> under the publications header
            next = heading
            while next is not None:
                if next.name == 'ol':
                    return pub_list_url, [strip_whitespace(li.text.replace('View Details', '').replace('Citation:', ''))
                                          for li in css_select(next, 'div.citation')]
                next = next.next_element
    return None, None


def scrape_harvard():
    return scrape_professors(school_name="Harvard",
                             directory_url='http://www.hbs.edu/faculty/Pages/browse.aspx',
                             extracts_faculty_urls=HrefListSelector('div.faculty-item a'),
                             extracts_title=Selector('p.faculty-title'),
                             extracts_name=Selector('h1.author'),
                             extracts_cv_url=HrefSelector('div.faculty-navigation div.links a',
                                                          'Curriculum Vitae', 'CV'),
                             extracts_personal_url=HrefSelector('div.faculty-navigation div.links a',
                                                                'Personal Website', 'Home Page'),
                             extracts_papers=get_papers)

if __name__ == '__main__':
    profs = scrape_harvard()