from professor import Professor, title_is_tenure_track
from web_util import get_tree, css_select, wait

def scrape_harvard():
    """ :return: a list of Professor objects for HBS """
    faculty = []
    # get the faculty index page
    tree = get_tree('http://www.hbs.edu/faculty/Pages/browse.aspx')
    # look for the faculty options listed in a select element
    for anchor in css_select(tree, 'div.faculty-item a'):
        url = anchor.get('href').strip()
        print url
        facultyId = url.split('=')[1]
        p = scrape_harvard_prof(facultyId)
        if p is not None:
            faculty.append(p)
    return faculty

def scrape_harvard_prof(facultyId):
    """ :return: a Professor object or None if it's not a tenure track faculty """
    wait()
    directory_url = 'http://www.hbs.edu/faculty/Pages/profile.aspx?facId=' + facultyId
    tree = get_tree(directory_url)
    try:
        job_title = css_select(tree, 'p.faculty-title')[0].text.strip()
    except AttributeError:
        print "WARNING: no job title found on " + directory_url
        return None
    if not title_is_tenure_track(job_title):
        return None
    name = css_select(tree, 'h1.author')[0].text.strip()
    print name
    # no cv is available on HBS
    return Professor(name=name, title=job_title, school='Harvard', staff_id=facultyId,
                     faculty_directory_url=directory_url)

if __name__ == '__main__':
    profs = scrape_harvard()
    print profs