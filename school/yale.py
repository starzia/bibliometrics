from professor_scraper import scrape_professors, Selector, HrefSelector
from web_util import css_select


# NOTE: one prof has a totally different page format that I had to manually scrape
# (http://faculty.som.yale.edu/lisakahn/)
# Look for "WARNING: job title not found"
def scrape_yale():
    return scrape_professors(school_name='Yale',
                             directory_url='http://som.yale.edu/faculty-research/faculty-directory',
                             extracts_faculty_urls=\
                                 lambda tree: ['http://som.yale.edu' + a.get('href').strip()
                                               for a in css_select(tree, 'h4.faculty--teaser-name a')],
                             extracts_name=Selector('h1.title'),
                             extracts_title=Selector('h2.sub-title'),
                             # for CV and GS, see: http://som.yale.edu/victoria-l-brescoll
                             extracts_cv_url=HrefSelector('ul.faculty--info-list li.url a', 'CV'),
                             # for website, see: http://som.yale.edu/nicholas-c-barberis
                             extracts_personal_url=HrefSelector('ul.faculty--info-list li.url a', 'Website'),
                             extracts_gscholar_url=HrefSelector('ul.faculty--info-list li.url a', 'Google Scholar'))

if __name__ == '__main__':
    profs = scrape_yale()
