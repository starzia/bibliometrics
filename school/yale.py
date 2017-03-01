from professor_scraper import scrape_professors
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


# NOTE: one prof has a totally different page format that I had to manually scrape
# (http://faculty.som.yale.edu/lisakahn/)
# Look for "WARNING: job title not found"
def scrape_yale():
    return scrape_professors(school_name='Yale',
                             directory_url='http://som.yale.edu/faculty-research/faculty-directory',
                             extracts_faculty_urls=HrefListSelector('h4.faculty--teaser-name a'),
                             extracts_name=Selector('h1.title'),
                             extracts_title=Selector('h2.sub-title'),
                             # for CV and GS, see: http://som.yale.edu/victoria-l-brescoll
                             extracts_cv_url=HrefSelector('ul.faculty--info-list li.url a', 'CV'),
                             # for website, see: http://som.yale.edu/nicholas-c-barberis
                             extracts_personal_url=HrefSelector('ul.faculty--info-list li.url a', 'Website'),
                             extracts_gscholar_url=HrefSelector('ul.faculty--info-list li.url a', 'Google Scholar'),
                             extracts_papers=get_papers)

if __name__ == '__main__':
    profs = scrape_yale()
