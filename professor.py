import os
import urllib
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

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
                 faculty_directory_url=None, personal_url=None):
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
                self.faculty_directory_url]

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
                         faculty_directory_url=get_from_row(row, 11))

    def merge(self, other_prof):
        """add any non-None attributes from the other_prof"""
        for attr, value in other_prof.__dict__.iteritems():
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

    def download_cv(self):
        wait()
        print("downloading CV for " + self.slug())
        if self.cv_url is None:
            print("WARNING: missing CV!")
            return

        global CV_PATH
        if not os.path.exists(CV_PATH):
            os.makedirs(CV_PATH)

        r = requests.get(self.cv_url)
        with open(CV_PATH + '/' + self.slug() + ".pdf", 'wb') as f:
            f.write(r.content)

    def find_google_scholar_page(self, selenium_driver):
        """NOTE: google is very proactive about blocking requests if it thinks you are a bot,
        so this sometimes results in a 503 error. """
        wait()
        # get search results page
        selenium_driver.get('https://scholar.google.com/scholar?q=author%%3A"%s"+%s' %
                        (urllib.parse.quote(self.simple_name()), self.school))
        try:
            selenium_driver.find_element_by_css_selector('div#gs_captcha_ccl')
        except NoSuchElementException:
            pass
        else:
            print("WARNING: got a CAPTCHA")
            # wait until CAPTCHA is gone
            WebDriverWait(selenium_driver, 99999).until(
                expected_conditions.invisibility_of_element_located((By.ID, "gs_captcha_ccl")))
        try:
            anchor = selenium_driver.find_element_by_css_selector('h4.gs_rt2 a')
            self.google_scholar_url = anchor.get_attribute('href')
        except NoSuchElementException:
            self.google_scholar_url = None