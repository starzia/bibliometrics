from professor_scraper import scrape_professors
from web_util import get_tree, css_select, Selector, HrefSelector, strip_whitespace


def get_faculty_urls(directory_url, main_directory_tree):  # ignore the main directory because it's paginated with ajax
    faculty_urls = []
    for dept in ['accounting', 'economics', 'finance', 'marketing', 'operations-information-technology',
                 'political-economy']:
        dept_tree = get_tree('https://www.gsb.stanford.edu/faculty-research/faculty/academic-areas/' + dept)
        # the first section is for Faculty, the second is for lecturers
        faculty_div = css_select(dept_tree, 'div.pane-faculty-filters-faculty-by-criteria')[0]
        for a in css_select(faculty_div, 'div.view-id-faculty_filters div.views-field-title a'):
            faculty_urls.append('https://www.gsb.stanford.edu' + a.get('href'))
    return faculty_urls


def get_name(tree):
    return ' '.join([span.text for span in css_select(tree, 'div.group-wrapper-name span')])


def get_papers(url, tree):
    # find the list of Journal Articles
    for heading in css_select(tree, 'div.view-gsb-publications-listing h2.title'):
        if 'Journal Articles' in heading.text:
            # look for the first <div class="view-content"> under the Journal Articles header
            candidate = heading
            while candidate is not None:
                if candidate.name == 'div' and 'view-content' in candidate.get('class'):
                    return url, [strip_whitespace(row.get_text()) for row in css_select(candidate, 'div.views-row')]
                candidate = candidate.next_element
    return None, None


def scrape_stanford():
    return scrape_professors(school_name="Stanford",
                             directory_url='https://www.gsb.stanford.edu/faculty-research/faculty',
                             extracts_faculty_urls=get_faculty_urls,
                             extracts_title=Selector('div.field-name-field-title-appointment'),
                             extracts_name=get_name,
                             extracts_cv_url=HrefSelector('div.field-name-field-file-single-public a', 'CV'),
                             extracts_personal_url=HrefSelector('div.field-name-field-link-website a',
                                                                          'Personal Website'),
                             extracts_gscholar_url=HrefSelector('div.field-name-field-file-single-public a',
                                                                                'Google Scholar'),
                             extracts_papers=get_papers)

if __name__ == '__main__':
    profs = scrape_stanford()