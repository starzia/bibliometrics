from professor_scraper import scrape_professors, Selector, HrefSelector
from web_util import css_select


def get_faculty_urls(tree):
    urls = []
    # find the "faculty by name" div, then look under it
    directory_div = False
    for div in css_select(tree, 'div.vc_row-fluid'):
        if directory_div:
            directory_div = div
            break
        for h4 in css_select(div, 'h4'):
            if 'FACULTY BY NAME' in h4.text:
                directory_div = True
    for a in css_select(directory_div, 'div.wpb_wrapper a'):
        if a.get('href') is not None:
            urls.append(a.get('href').strip())
    return urls


def scrape_upenn():
    return scrape_professors(school_name='UPenn',
                             directory_url='http://www.wharton.upenn.edu/faculty-directory/',
                             extracts_faculty_urls_from_tree=get_faculty_urls,
                             extracts_title_from_tree=Selector('ul.wfp-header-titles li:first-of-type'),
                             extracts_name_from_tree=Selector('div.wfp-header h1'),
                             extracts_cv_url_from_tree=HrefSelector('wfp-header-research a', 'CV'),
                             extracts_personal_url_from_tree=HrefSelector('wfp-header-research a', 'Personal Website'),
                             extracts_google_scholar_url_from_tree=HrefSelector('wfp-header-research a',
                                                                                'Google Scholar'))

if __name__ == '__main__':
    profs = scrape_upenn()