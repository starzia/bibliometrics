from professor_scraper import scrape_professors, Selector, HrefSelector
from web_util import css_select


def get_kellogg_faculty_urls(tree):
    """Parse a drop-down selection."""
    urls = []
    for option in css_select(tree, 'select#plcprimarymaincontent_1_selBrowseByName option'):
        if (option.get('value') != ''):
            netId = option.get('value')
            urls.append('http://www.kellogg.northwestern.edu/Faculty/Faculty_Search_Results.aspx?netid=' + netId)
    return urls


def scrape_kellogg():
    return scrape_professors(school_name="Northwestern",
                             directory_url='http://www.kellogg.northwestern.edu/faculty/advanced_search.aspx',
                             extracts_faculty_urls=get_kellogg_faculty_urls,
                             extracts_title=Selector('span#lblTitle'),
                             extracts_name=Selector('span#lblName'),
                             extracts_cv_url=HrefSelector('div#sideNav3 a', 'Download Vita (pdf)'))

if __name__ == '__main__':
    profs = scrape_kellogg()