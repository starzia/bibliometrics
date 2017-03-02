from professor_scraper import scrape_professors
from web_util import Selector, HrefSelector, HrefListSelector, get_tree, css_select, strip_whitespace
import editdistance


get_name = Selector('div.faculty-bio-info h1')


library_directory_url = 'https://www.lib.uchicago.edu/research/help/bibliographies/busfac/'
library_directory_tree = None


# UChicago's library has a directory of Business school bibiographies at
# https://www.lib.uchicago.edu/research/help/bibliographies/busfac/
def get_papers(faculty_url, tree):
    name = get_name(tree)
    # download faculty directory, if not already downloaded
    global library_directory_tree
    if not library_directory_tree:
        library_directory_tree = get_tree(library_directory_url)
    # iterate through faculty names, looking for the best match
    anchors = css_select(library_directory_tree, 'table.table-striped a')
    closest_match = min(anchors, key=lambda x: editdistance.eval(name, strip_whitespace(x.text)))
    # require that closest match be pretty close to accept it
    if editdistance.eval(name, closest_match.text) > 3:  # 3 characters would allow for a missing initial and period
        return None, None
    # download bibliography page
    bib_url = closest_match.get('href')
    bib_tree = get_tree(bib_url)
    # find the "Published Works" section
    for heading in css_select(bib_tree, 'div.rich-text h2'):
        if 'Published' in heading.text:
            # keep collecting the publication divs until we get to the next <H2>
            papers = []
            next = heading.next_element
            while next:
                if next.name == 'p':
                    citation = strip_whitespace(next.text)
                    # drop trailing link
                    citation = citation.split('http://')[0]
                    if len(citation) > 0:
                        papers.append(citation)
                elif next.name == 'h2':
                    break
                next = next.next_element
            return bib_url, papers
    return None, None


def scrape_uchicago():
    return scrape_professors(
            school_name="Chicago",
            directory_url='https://www.chicagobooth.edu/faculty/directory',
            extracts_faculty_urls=HrefListSelector('div.faculty-listing-name a'),
            extracts_title=Selector('div.faculty-bio-info h2'),
            extracts_name=get_name,
            extracts_cv_url=HrefSelector('ul.resource-list a', 'Curriculum Vitae'),
            extracts_personal_url=HrefSelector('p.faculty-link-website a', 'Personal Website'),
            extracts_papers=get_papers)

if __name__ == '__main__':
    profs = scrape_uchicago()