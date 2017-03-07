import urllib
import time
import re
from professor import Professor
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, InvalidElementStateException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium import webdriver

from web_util import wait, tree_from_string, css_select, Selector
from typing import List


STARTING_YEAR = '2007'


def none_to_empty(obj):
    return obj if obj else ''


def empty_to_none(str):
    return str if len(str) > 0 else None


def get_from_array(arr, idx):
    if idx >= len(arr):
        return None
    else:
        return empty_to_none(arr[idx])


class Paper:
    def __init__(self, title, authors, venue, year, scholar_citations, wos_citations=None, id=None):
        self.title = title
        self.authors = authors
        self.venue = venue
        self.year = year
        self.scholar_citations = scholar_citations
        self.wos_citations = wos_citations
        self.id = id

    def __str__(self):
        return '\t'.join([self.authors, self.title, self.venue, self.year, self.scholar_citations,
                          none_to_empty(self.wos_citations), none_to_empty(self.id)])

    def pretty_citation(self):
        return '. '.join([self.authors, self.title, self.venue, self.year])

    @classmethod
    def from_string(cls, string):
        s = string.split('\t')
        return Paper(authors = s[0],
                     title = s[1],
                     venue = s[2],
                     year = s[3],
                     scholar_citations = get_from_array(s, 4),
                     wos_citations = get_from_array(s, 5),
                     id = get_from_array(s, 6))

class GoogleScholar:
    def __init__(self, executable_path=None):
        self.selenium_driver = \
            webdriver.Firefox(executable_path=executable_path) if executable_path else webdriver.Firefox()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.selenium_driver.quit()

    def wait_for_captchas(self):
        """Sleep if a captcha or error page is shown, otherwise return immediately."""

        # detect the javascript Captcha that is embedded in the search results page
        try:
            self.selenium_driver.find_element_by_css_selector('div#gs_captcha_ccl')
        except NoSuchElementException:
            pass
        else:
            print("WARNING: got a Javascript CAPTCHA")
            # wait until CAPTCHA is gone
            WebDriverWait(self.selenium_driver, 99999).until(
                expected_conditions.invisibility_of_element_located((By.ID, "gs_captcha_ccl")))

        # detect the IP-based Captcha that redirects you to ipv4.google.com/sorry/index and is more old-school looking
        already_failed = False
        while 'google.com/sorry' in self.selenium_driver.current_url:
            if not already_failed:
                print("WARNING: got a form CAPTCHA")
                already_failed = True
            time.sleep(1)
        if already_failed:
            self.wait_for_captchas()

        # detect 403 error that refers to Terms of Service
        already_failed = False
        while True:
            try:
                title = self.selenium_driver.find_element_by_css_selector('title').text
            except NoSuchElementException:
                break
            if 'Error' not in title and 'Sorry' not in title:
                break
            if not already_failed:
                print("WARNING: got an error page")
                already_failed = True
            time.sleep(1)
        if already_failed:
            self.wait_for_captchas()

    def get_page(self, url):
        wait()
        self.selenium_driver.get(url)
        self.wait_for_captchas()

    def find_google_scholar_page(self, prof: Professor):
        # get search results page
        self.get_page('https://scholar.google.com/scholar?q=author%%3A"%s"+%s' %
                      (urllib.parse.quote(prof.simple_name()), prof.school))
        # look for a matching user profile
        try:
            anchor = self.selenium_driver.find_element_by_css_selector('h4.gs_rt2 a')
            return anchor.get_attribute('href')
        except NoSuchElementException:
            return None

    # eg., see https://scholar.google.com/citations?user=VGoSakQAAAAJ&hl=en&oi=ao
    def scrape_profile(self, author_url) -> List[Paper]:
        self.get_page(author_url)
        # click "show more" button until it disappears
        while True:
            try:
                for button in self.selenium_driver.find_elements_by_css_selector('button'):
                    if button.text == 'Show more':
                        button.click()
                        self.wait_for_captchas()
                        wait()
            except (NoSuchElementException, ElementNotVisibleException, InvalidElementStateException):
                # we expect to see an InvalidElementStateException if the button is disabled after clicking it
                break
        # load the page in Beautiful Soup for easier parsing
        tree = tree_from_string(self.selenium_driver.page_source)
        # scrape the list of papers
        papers = []
        for row in css_select(tree, 'tr.gsc_a_tr'):
            title = Selector('td.gsc_a_t a')(row)
            authors_and_venue = css_select(row, 'div.gs_gray')
            author = authors_and_venue[0].text
            venue = authors_and_venue[1].text
            year = Selector('td.gsc_a_y')(row)
            citation_count = Selector('td.gsc_a_c a.gsc_a_ac')(row)
            # look for strikeout (cross-out) over citation count, indicating that it's a dupe
            if Selector('td.gsc_a_c a.gsc_a_acm')(row):
                continue
            papers.append(Paper(title, author, venue, year, citation_count))
        return papers

    def scrape_search_results(self, prof: Professor) -> List[Paper]:
        """In this case, we are saving all articles, even if we are not sure that they match the author.
        We only search in the past ten years (2007 and later) and only include the first 100 pages of results,
        and only papers that have at least one citation in Google Scholar (to save us some time)."""
        # parse each page of results, up to at most 1000 articles (100 pages)
        papers = []
        # for each page of results
        for start in range(0, 1000, 10):
            result_row_info = []
            # get search results page
            self.get_page(
                'https://scholar.google.com/scholar?start=%d&as_ylo=%s&q=author%%3A"%s"+%s' %
                (start, STARTING_YEAR, urllib.parse.quote(prof.simple_name()), prof.school))

            # We get the GS and WoS citation counts from the search results page
            # We get the full citation information by virtually clicking the "cite" link for each article
            tree = tree_from_string(self.selenium_driver.page_source)
            for row in css_select(tree, 'div.gs_r div.gs_ri'):
                scholar_citations = None
                wos_citations = None
                citation_id = None
                for link in css_select(row, 'div.gs_fl a'):
                    if 'Cited by' in link.text:
                        scholar_citations = link.text.split(' ')[-1]
                    elif 'Web of Science:' in link.text:
                        wos_citations = link.text.split(': ')[-1]
                    elif link.get('onclick') and 'return gs_ocit' in link.get('onclick'):
                        citation_id = link.get('onclick').split("'")[1]
                # ignore papers with no citations
                if not scholar_citations:
                    break
                result_row_info.append({'scholar_citations': scholar_citations,
                                        'wos_citations': wos_citations,
                                        'citation_id': citation_id})
            # stop when we've gone past the end of results
            if len(result_row_info) == 0:
                break

            # fetch each citation and pick out the Chicago format because it has full firstnames
            # and includes all the author names (or at least more of them before using "et al."
            # eg., https://scholar.google.com/scholar?q=info:J2Uvx00ui50J:scholar.google.com/&output=cite&scirp=1&hl=en
            for r in result_row_info:
                self.get_page('https://scholar.google.com/scholar?q=info:%s:scholar.google.com/'
                              '&output=cite&scirp=1&hl=en' % r['citation_id'])
                # the third row in the table contains the Chicago-style citation
                citation = self.selenium_driver.find_elements_by_css_selector('td')[2].text
                try:
                    # first, look for the year inside parens
                    year = re.findall(r"\(([12][0-9]{3})\)", citation)[0]
                except IndexError:
                    # if no year exists inside parens, then take the last number that looks like a year
                    year = re.findall(r"[12][0-9]{3}", citation)[-1]
                # look for the first period that is not part of a middle initial
                match = re.search(r"\w{2}\. ", citation)
                if not match:
                    # otherwise, just take the first period as in: Al-Najjar, Nabil I. "A bayesian framework for precautionary policies." (2013).
                    match = re.search(r"\. ", citation)
                authors = citation[:match.end()]
                # venue is in italics
                try:
                    venue = self.selenium_driver.find_elements_by_css_selector('td')[2]\
                                                .find_element_by_css_selector('i').text
                except NoSuchElementException:
                    # this is probably a working paper
                    continue
                match = re.findall(r"\"(.*)\"", citation)  # article titles are inside quotes
                if len(match) == 0:
                    # this is a book, which we don't record
                    continue
                title = match[0]
                papers.append(Paper(title=title, authors=authors, venue=venue, year=year,
                                    scholar_citations=r['scholar_citations'],
                                    wos_citations=r['wos_citations'], id=r['citation_id']))
        return papers

if __name__ == '__main__':
    # for some reason, running this in the IDE requires me to set the geckodriver path
    with GoogleScholar('/usr/local/bin/geckodriver') as scholar:
        # res = scholar.scrape_scholar_profile('https://scholar.google.com/citations?user=VGoSakQAAAAJ&hl=en&oi=ao')
        print(scholar.scrape_search_results(Professor(school='Northwestern', name='Nabil Al-Najjar')))
