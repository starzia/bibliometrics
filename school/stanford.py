from professor_scraper import scrape_professors, Selector, HrefSelector
from web_util import get_tree, css_select


def get_faculty_urls(main_directory_tree):  # ignore the main directory because it's paginated with ajax
    faculty_urls = []
    for dept in ['accounting', 'economics', 'finance', 'marketing', 'operations-information-technology', 'political-economy']:
        dept_tree = get_tree('https://www.gsb.stanford.edu/faculty-research/faculty/academic-areas/' + dept)
        for a in css_select(dept_tree, 'div.view-id-faculty_filters div.views-field-title a'):
            faculty_urls.append('https://www.gsb.stanford.edu' + a.get('href'))
    return faculty_urls


def get_name(tree):
    return ' '.join([span.text for span in css_select(tree, 'div.group-wrapper-name span')])


def scrape_stanford():
    return scrape_professors(school_name="Stanford",
                             directory_url='https://www.gsb.stanford.edu/faculty-research/faculty',
                             extracts_faculty_urls_from_tree=get_faculty_urls,
                             extracts_title_from_tree=Selector('div.field-name-field-title-appointment'),
                             extracts_name_from_tree=get_name,
                             extracts_cv_url_from_tree=HrefSelector('div.field-name-field-file-single-public a', 'CV'),
                             extracts_personal_url_from_tree=HrefSelector('div.field-name-field-link-website a', 'Personal Website'))

if __name__ == '__main__':
    profs = scrape_stanford()