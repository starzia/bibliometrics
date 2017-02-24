from professor_scraper import scrape_professors, Selector, HrefSelector
from web_util import css_select


def scrape_yale():
    return scrape_professors(school_name='Yale',
                             directory_url='http://som.yale.edu/faculty-research/faculty-directory',
                             extracts_faculty_urls_from_tree=\
                                 lambda tree: ['http://som.yale.edu' + a.get('href').strip()
                                               for a in css_select(tree, 'h4.faculty--teaser-name a')],
                             extracts_title_from_tree=Selector('div.title h3h1#page-title'),
                             extracts_name_from_tree=Selector('h2.sub-title'),
                             # for CV and GS, see: http://som.yale.edu/victoria-l-brescoll
                             extracts_cv_url_from_tree=HrefSelector('ul.faculty--info-list li.url a', 'CV'),
                             # for website, see: http://som.yale.edu/nicholas-c-barberis
                             extracts_personal_url_from_tree=HrefSelector('ul.faculty--info-list li.url a', 'Website'),
                             extracts_google_scholar_url_from_tree=HrefSelector('ul.faculty--info-list li.url a', 'Google Scholar'))

if __name__ == '__main__':
    profs = scrape_yale()