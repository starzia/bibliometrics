from professor_scraper import scrape_professors
from web_util import css_select

def get_kellogg_faculty_urls(tree):
    urls = []
    for option in css_select(tree, 'select#plcprimarymaincontent_1_selBrowseByName option'):
        if (option.get('value') != ''):
            netId = option.get('value')
            urls.append('http://www.kellogg.northwestern.edu/Faculty/Faculty_Search_Results.aspx?netid=' + netId)
    return urls

def get_kellogg_faculty_cv_url(tree):
    for a in css_select(tree, 'div#sideNav3 a'):
        if "Download Vita (pdf)" in a.text:
            return a.get('href')
    return None

def scrape_kellogg():
    return scrape_professors(school_name="Kellogg",
                             directory_url='http://www.kellogg.northwestern.edu/faculty/advanced_search.aspx',
                             extracts_faculty_urls_from_tree=get_kellogg_faculty_urls,
                             job_title_selector='span#lblTitle',
                             name_selector='span#lblName',
                             extracts_cv_url_from_tree=get_kellogg_faculty_cv_url)

if __name__ == '__main__':
    profs = scrape_kellogg()