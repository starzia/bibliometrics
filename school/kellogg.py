from professor import Professor, title_is_tenure_track
from web_util import get_tree, css_select

def scrape_kellogg():
    """
    :return: a list of faculty objects for the Kellogg School of Management
    """
    faculty = []
    # get the faculty index page
    tree = get_tree('http://www.kellogg.northwestern.edu/faculty/advanced_search.aspx')
    # look for the faculty options listed in a select element
    for option in css_select(tree, 'select#plcprimarymaincontent_1_selBrowseByName option'):
        if (option.get('value') != ''):
            print option.get('value') + ": " + option.text
            netId = option.get('value')
            f = scrape_kellogg_faculty(netId)
            if f is not None:
                faculty.append(f)
    return faculty

def scrape_kellogg_faculty(netId):
    """ :return: a faculty object or None if it's not a tenure track faculty """
    tree = get_tree('http://www.kellogg.northwestern.edu/Faculty/Faculty_Search_Results.aspx?netid=' + netId)
    job_title = css_select(tree, 'span#lblTitle')[0].text
    if not title_is_tenure_track(job_title):
        return None
    name = css_select(tree, 'span#lblName')[0].text
    cv_link = None
    for a in css_select(tree, 'div#sideNav3 a'):
        if "Download Vita (pdf)" in a.text:
            cv_link = a.get('href')
    return Professor(name=name, title=job_title, cv_url=cv_link, school='Kellogg', staff_id=netId)