from professor_scraper import scrape_professors
from web_util import Selector, HrefSelector, HrefListSelector, strip_whitespace, css_select


def get_papers(url, tree):
    papers = []
    # find the list of divs for journal publications
    for heading in css_select(tree, 'h3'):
        if 'Journal articles' in heading.text:
            # keep collecting the publication divs until we get to the next <H3>
            next = heading
            while next is not None:
                if next.name == 'p':
                    papers.append(strip_whitespace(next.text))
                elif next.name == 'div' and 'Awards and Honors' in next.text:
                    break
                next = next.next_element
    return url+'#research', papers


def scrape_columbia():
    return scrape_professors(school_name='Columbia',
                             directory_url='http://www8.gsb.columbia.edu/faculty-research/faculty-directory?full_time=y&division=All&op=Search',
                             extracts_faculty_urls=HrefListSelector('div.name a'),
                             extracts_name=Selector('h1.primary-heading'),
                             extracts_title=Selector('span.affiliation-title'),
                             # for CV and personal website, see http://www8.gsb.columbia.edu/cbs-directory/detail/ea1
                             extracts_cv_url=HrefSelector('div#contact_info a', 'Curriculum Vitae'),
                             extracts_personal_url=HrefSelector('div#contact_info a', 'Personal Website'),
                             extracts_gscholar_url=None,
                             extracts_papers=get_papers)

if __name__ == '__main__':
    profs = scrape_columbia()
