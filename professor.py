from unidecode import unidecode

from web_util import *
from google_sheets_util import get_from_row


def lower_alpha(str):
    """ :return: a transformation of the string including only lowercase letters and underscore"""
    return ''.join(char for char in str.lower().replace(' ', '_') if char.isalnum() or char == '_')


def get_from_row(row, column_idx):
    """get the value from the specified column index, or return None if it's empty"""
    if (len(row) <= column_idx) or row[column_idx] == "":
        return None
    return row[column_idx]


class Professor:
    def __init__(self, school, name, title=None, cv_url=None, graduation_year=None,
                 google_scholar_url=None, graduation_school=None, alt_name=None,
                 faculty_directory_url=None, personal_url=None, paper_list_url=None):
        self.school = school
        self.name = name
        self.title = title
        self.cv_url = cv_url
        self.graduation_year = graduation_year
        self.graduation_school = graduation_school
        self.personal_url = personal_url
        self.google_scholar_url = google_scholar_url
        self.alt_name = alt_name
        self.faculty_directory_url = faculty_directory_url
        self.paper_list_url = paper_list_url

    def spreadsheet_row(self):
        return [self.slug(),
                self.school,
                self.name,
                self.title,
                self.cv_url,
                self.graduation_year,
                self.personal_url,
                None,  # hidden
                self.google_scholar_url,
                self.alt_name,
                self.graduation_school,
                self.faculty_directory_url,
                self.paper_list_url]

    @classmethod
    def from_spreadsheet_row(cls, row):
        return Professor(name=get_from_row(row, 2),
                         school=get_from_row(row, 1),
                         title=get_from_row(row, 3),
                         cv_url=get_from_row(row, 4),
                         graduation_year=get_from_row(row, 5),
                         personal_url=get_from_row(row, 6),
                         google_scholar_url=get_from_row(row, 8),
                         alt_name=get_from_row(row, 9),
                         graduation_school=get_from_row(row, 10),
                         faculty_directory_url=get_from_row(row, 11),
                         paper_list_url=get_from_row(row, 12))

    def merge(self, other_prof):
        """add any non-None attributes from the other_prof"""
        for attr, value in other_prof.__dict__.items():
            if value is not None and getattr(self, attr) is None:
                setattr(self, attr, value)

    def __repr__(self):
        import pprint
        return pprint.pformat(vars(self), indent=4, width=1)

    def slug(self):
        """ :return: a human-readable string identifying the professor, to be used to filenames and such. """
        return lower_alpha(self.school + ' ' + self.name)

    def simple_name(self):
        """:return: "firstname lastname" and also removed any character diacritics (accents)."""
        parts = self.name.split(' ')
        return unidecode("%s %s" % (parts[0], parts[-1]))


    # TODO: extract PDFs from google docs? https://sites.google.com/site/kbaldigacoffman/resume
    def parse_personal_website(self):
        """Looks for links to a CV and to Google Scholar on the Professor's personal website.
        We check for an updated CV on the personal page even if we already found one on the faculty directory."""
        if self.personal_url is not None:
            wait()
            # look for links on the main page labelled "CV" or similar
            tree = get_tree(self.personal_url)
            cv_url = HrefSelector('a', 'CV', 'C.V.', 'Vita', 'Resume')(self.personal_url, tree)
            if cv_url is not None:
                # check whether pdf link is present on the cv page, eg. see http://www.fanyinzheng.com/
                if '.pdf' not in cv_url:
                    tree2 = get_tree(cv_url)
                    for maybe_pdf_url in HrefListSelector('a')(cv_url, tree2):
                        if maybe_pdf_url is not None and 'pdf' in maybe_pdf_url:
                            cv_url = maybe_pdf_url
                # only replace the an existing CV link if it's a PDF
                if self.cv_url is None or cv_url.endswith('.pdf'):
                    self.cv_url = cv_url
                    print('%s: found CV %s' % (self.slug(), self.cv_url))
            # look for links to 'scholar.google.com'
            if self.google_scholar_url is None:
                for a in css_select(tree, 'a'):
                    if a.get('href') is not None and 'scholar.google.com/citations?user=' in a.get('href'):
                        gs_url = a.get('href')
                        print('%s: found Google Scholar page %s' % (self.slug(), self.google_scholar_url))
                        self.google_scholar_url = gs_url

if __name__ == '__main__':
    # this is just a test case
    p = Professor(school='Columbia', name='F. Zhang', title="Professor", personal_url='http://www.fanyinzheng.com')
    p.parse_personal_website()