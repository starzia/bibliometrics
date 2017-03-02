from professor_scraper import scrape_professors
from web_util import css_select, Selector, HrefSelector, get_json, tree_from_string


def get_faculty_urls(directory_url, tree):
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


def get_papers(url, tree):
    # An ajax call returns JSON with publication info,
    # eg., see https://fnce.wharton.upenn.edu/profile/abel/#research
    url = css_select(tree, 'link[rel="canonical"]')[0].get('href')
    if url.endswith('/'):
        # extract from https://statistics.wharton.upenn.edu/profile/bhaswar/
        user_id = url.split('/')[-2]
    else:
        # extract from https://www.wharton.upenn.edu/faculty/binsbergen.cfm
        user_id = url.replace('.cfm', '').split('/')[-1]
    json = get_json('https://faculty.wharton.upenn.edu/wp-json/wfp/v2/publication/?author=%s&per_page=500&page=1' % user_id)
    if 'data' not in json:
        return None, None
    citations = []
    for paper in json['data']:
        if paper['type'] == 'wfp_pubpubpaper':  # published papers only
            # The 'citation' attribute contains an html-formatted citation. We just convert it to plain text.
            citations.append(tree_from_string(paper['citation']).get_text())
    return url + '#research', citations


def scrape_upenn():
    return scrape_professors(school_name='UPenn',
                             directory_url='https://www.wharton.upenn.edu/faculty-directory/',
                             extracts_faculty_urls=get_faculty_urls,
                             extracts_title=Selector('ul.wfp-header-titles li:nth-of-type(1)'),
                             extracts_name=Selector('div.wfp-header h1'),
                             extracts_cv_url=HrefSelector('div.wfp-header-research a', 'CV'),
                             extracts_personal_url=HrefSelector('div.wfp-header-research a', 'Personal Website'),
                             extracts_gscholar_url=HrefSelector('div.wfp-header-research a', 'Google Scholar'),
                             extracts_papers=get_papers)

if __name__ == '__main__':
    profs = scrape_upenn()
