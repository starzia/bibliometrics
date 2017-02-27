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
        url = a.get('href')
        if url is not None:
            if "wharton.upenn.edu" in url:
                urls.append(url.strip())
            else:
                "WARNING: dropping non-Wharton faculty: "+url
    return urls


def scrape_upenn():
    return scrape_professors(school_name='UPenn',
                             directory_url='https://www.wharton.upenn.edu/faculty-directory/',
                             extracts_faculty_urls=get_faculty_urls,
                             extracts_title=Selector('ul.wfp-header-titles li:nth-of-type(1)'),
                             extracts_name=Selector('div.wfp-header h1'),
                             extracts_cv_url=HrefSelector('wfp-header-research a', 'CV'),
                             extracts_personal_url=HrefSelector('wfp-header-research a', 'Personal Website'),
                             extracts_gscholar_url=HrefSelector('wfp-header-research a',
                                                                                'Google Scholar'))

if __name__ == '__main__':
    profs = scrape_upenn()