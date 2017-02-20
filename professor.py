import requests
import os
import urllib

from scraper import wait
from scraper import get_tree
from scraper import css_select

def lower_alpha(str):
    """ :return: a transformation of the string including only lowercase letters and underscore"""
    return ''.join(char for char in str.lower().replace(' ', '_') if char.isalnum() or char is '_')

class Professor:
    def __init__(self, school, name, title=None, cv_url=None, graduation_year=None, staff_id=None, google_scholar_url=None):
        self.school = school
        self.name = name
        self.title = title
        self.cv_url = cv_url
        self.graduation_year = graduation_year
        self.staff_id = staff_id
        self.google_scholar_url = google_scholar_url

    def slug(self):
        """ :return: a human-readable string identifying the professor, to be used to filenames and such. """
        return lower_alpha(self.school + '_' + self.name)

    def download_cv(self):
        wait()
        print "downloading CV for " + self.slug()
        if self.cv_url is None:
            print "WARNING: missing CV!"
            return

        global CV_PATH
        if not os.path.exists(CV_PATH):
            os.makedirs(CV_PATH)

        r = requests.get(self.cv_url)
        with open(CV_PATH + '/' + self.slug() + ".pdf", 'wb') as f:
            f.write(r.content)

    def find_google_scholar_page(self):
        """NOTE: google is very proactive about blocking requests if it thinks you are a bot,
        so this sometimes results in a 503 error. """
        wait()
        # get search results page
        tree = get_tree('https://scholar.google.com/scholar?q=author%%3A"%s"+%s' %
                        (urllib.quote_plus(self.name), self.school))
        anchors = css_select(tree, 'h4.gs_rt2 a')
        if len(anchors) > 0:
            if len(anchors) > 1:
                print "WARNING: multiple author pages found for %s" % self.name
            self.google_scholar_url = anchors[0].get('href')
        else:
            self.google_scholar_url = None