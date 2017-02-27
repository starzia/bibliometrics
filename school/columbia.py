from professor_scraper import scrape_professors, Selector, HrefSelector, HrefListSelector


def scrape_columbia():
    return scrape_professors(school_name='Columbia',
                             directory_url='http://www8.gsb.columbia.edu/faculty-research/faculty-directory?full_time=y&division=All&op=Search',
                             extracts_faculty_urls=HrefListSelector('div.name a'),
                             extracts_name=Selector('h1.primary-heading'),
                             extracts_title=Selector('span.affiliation-title'),
                             # for CV and personal website, see http://www8.gsb.columbia.edu/cbs-directory/detail/ea1
                             extracts_cv_url=HrefSelector('div#contact_info a', 'Curriculum Vitae'),
                             extracts_personal_url=HrefSelector('div#contact_info a', 'Personal Website'),
                             extracts_gscholar_url=None)

if __name__ == '__main__':
    profs = scrape_columbia()
