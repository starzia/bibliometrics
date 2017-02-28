from professor_scraper import scrape_professors
from web_util import css_select, Selector, HrefSelector, strip_whitespace


def get_kellogg_faculty_urls(directory_url, tree):
    """Parse a drop-down selection."""
    urls = []
    for option in css_select(tree, 'select#plcprimarymaincontent_1_selBrowseByName option'):
        if option.get('value') != '':
            net_id = option.get('value')
            urls.append('http://www.kellogg.northwestern.edu/Faculty/Faculty_Search_Results.aspx?netid=' + net_id)
    return urls


def get_papers(faculty_url, tree):
    for e in css_select(tree, 'div.leftResearch div.entries'):
        # check that we're in the right section
        if e.previous_sibling['class'] == 'tabSubheading' and e.previous_sibling.text != 'Articles':
            break
        paper_list = []
        for c in css_select(e, 'div.entry div.copy'):
            citation = c.text
            # some articles have an abstract, which I want to ignore
            for abstract in css_select(c, 'div'):
                citation = citation.replace(abstract.text, '')
            paper_list.append(strip_whitespace(citation))
        return faculty_url + '#research', paper_list
    return None, None


def scrape_kellogg():
    return scrape_professors(school_name="Northwestern",
                             directory_url='http://www.kellogg.northwestern.edu/faculty/advanced_search.aspx',
                             extracts_faculty_urls=get_kellogg_faculty_urls,
                             extracts_title=Selector('span#lblTitle'),
                             extracts_name=Selector('span#lblName'),
                             extracts_cv_url=HrefSelector('div#sideNav3 a', 'Download Vita'),
                             extracts_papers=get_papers)

if __name__ == '__main__':
    profs = scrape_kellogg()