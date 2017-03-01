from professor_scraper import scrape_professors, scrape_professor
from web_util import Selector, HrefSelector, HrefListSelector, css_select, get_tree


# eg., see http://som.yale.edu/jason-abaluck
#      and http://som.yale.edu/publications/faculty/jason.abaluck-at-yale.edu
def get_papers(url, tree):
    # find the link to "More publications
    more_pubs_url = HrefSelector('a.right-arrow', 'More Publications')(url, tree)
    if more_pubs_url is not None:
        papers = []
        p_tree = get_tree(more_pubs_url)
        for article in css_select(p_tree, 'article.publication--teaser'):
            if 'Article' in Selector('div.publication--teaser-type')(article):
                p_title = Selector('h2 a')(article)
                p_year = Selector('div.publication--teaser-year')(article)
                p_authors = Selector('div.publication--teaser-authors')(article)
                p_journal = Selector('div.publication--teaser-journal')(article)
                papers.append('%s. "%s." %s (%s).' % (p_authors, p_title, p_journal, p_year))
        return more_pubs_url, papers
    return None, None


econ_faculty_urls = []


def get_title(tree):
    # we hook in here to keep track of econ professors having more-detailed econ dept pages
    econ_page = HrefSelector('a.lg-arrow-blue', 'Department of Economics website')('http://localhost', tree)
    if econ_page is not None:
        econ_faculty_urls.append(econ_page)
        # return an empty job title so that the prof will be dropped by the first scrape
        return ''
    return Selector('h2.sub-title')(tree)


# NOTE: one prof has a totally different page format that I had to manually scrape
# (http://faculty.som.yale.edu/lisakahn/)
# Look for "WARNING: job title not found"
def scrape_yale():
    # We do two passes because Yale's econ dept has its own set of pages with a different format.
    # Yale's econ profs have skeleton profiles in their school directory and more detailed ones in the dept directory.
    # eg., http://som.yale.edu/dirk-bergemann
    #  and http://economics.yale.edu/people/dirk-bergemann

    # as a side-effect, this scrape will populate the econ_faculty_to_urls dictionary
    profs = scrape_professors(
                             school_name='Yale',
                             directory_url='http://som.yale.edu/faculty-research/faculty-directory',
                             extracts_faculty_urls=HrefListSelector('h4.faculty--teaser-name a'),
                             extracts_name=Selector('h1.title'),
                             extracts_title=get_title,
                             # for CV and GS, see: http://som.yale.edu/victoria-l-brescoll
                             extracts_cv_url=HrefSelector('ul.faculty--info-list li.url a', 'CV'),
                             # for website, see: http://som.yale.edu/nicholas-c-barberis
                             extracts_personal_url=HrefSelector('ul.faculty--info-list li.url a', 'Website'),
                             extracts_gscholar_url=HrefSelector('ul.faculty--info-list li.url a', 'Google Scholar'),
                             extracts_papers=get_papers)
    # Now scrape the econ profs from the econ dept website
    econ_profs = scrape_professors(
                             school_name='Yale',
                             directory_url='http://som.yale.edu/faculty-research/faculty-directory',  # not used
                             extracts_faculty_urls=lambda url, tree: econ_faculty_urls,
                             extracts_name=Selector('h1.title'),
                             extracts_title=Selector('div.group-right div.field-item'),
                             extracts_cv_url=HrefSelector('div.group-right div.field-item a', 'CV'),
                             extracts_personal_url=HrefSelector('div.group-right div.field-item a', 'Website'))
    return profs + econ_profs


if __name__ == '__main__':
    profs = scrape_yale()
