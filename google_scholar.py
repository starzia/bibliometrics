import urllib
import time
from professor import Professor
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, InvalidElementStateException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium import webdriver

from web_util import wait, tree_from_string, css_select, Selector, HrefSelector, get_tree
from typing import List


class Paper:
    def __init__(self, title, authors, venue, year, citation_count):
        self.title = title
        self.authors = authors
        self.venue = venue
        self.year = year
        self.citation_count = citation_count

    def __str__(self):
        elements = [self.authors, self.title, self.venue, self.year, self.citation_count]
        return '\t'.join(elements)


class GoogleScholar:
    def __init__(self, executable_path=None):
        self.selenium_driver = \
            webdriver.Firefox(executable_path=executable_path) if executable_path else webdriver.Firefox()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.selenium_driver.quit()

    def wait_for_captchas(self):
        """Sleep if a captcha is shown, otherwise return immediately."""

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
        already_printed = False
        while 'google.com/sorry' in self.selenium_driver.current_url:
            if not already_printed:
                print("WARNING: got a form CAPTCHA")
                already_printed = True
            time.sleep(1)

    def find_google_scholar_page(self, prof: Professor):
        wait()
        # get search results page
        self.selenium_driver.get('https://scholar.google.com/scholar?q=author%%3A"%s"+%s' %
                                 (urllib.parse.quote(prof.simple_name()), prof.school))
        self.wait_for_captchas()
        # look for a matching user profile
        try:
            anchor = self.selenium_driver.find_element_by_css_selector('h4.gs_rt2 a')
            return anchor.get_attribute('href')
        except NoSuchElementException:
            return None

    # eg., see https://scholar.google.com/citations?user=VGoSakQAAAAJ&hl=en&oi=ao
    def scrape_papers(self, author_url) -> List[Paper]:
        wait()
        self.selenium_driver.get(author_url)
        self.wait_for_captchas()
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

    def download_search_results(self, prof: Professor):
        wait()
        # get search results page
        self.selenium_driver.get('https://scholar.google.com/scholar?q="%s"' % (urllib.parse.quote(prof.simple_name())))
        self.wait_for_captchas()
        # parse each page of results
        while True:
            next_link = self.selenium_driver.find_element_by_css_selector(TODO)
            # We get the GS and WoS citation counts from the search results page
            # We get the full citation information by virtually clicking the "cite" link for each article
            row_info = []
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
                    elif 'return gs_ocit' in link.get('onclick'):
                        citation_id = link.get('onclick').split("'")[1]
                row_info.append({'scholar_citations':scholar_citations,
                                 'wos_citations':wos_citations,
                                 'citation_id':citation_id})

            # fetch each citation and pick out the Chicago format because it has full firstnames
            for row in row_info:
                wait()
                self.selenium_driver.get('https://scholar.google.com/scholar?q=info:%s:scholar.google.com/'
                                         '&output=cite&scirp=1&hl=en' % row['citation_id'])
                TODO

            # fetch the next page, or break if at the end
            if next_link:
                wait()
                next_link.click()
                self.wait_for_captchas()
            else:
                break
        # write results
        TODO

if __name__ == '__main__':
    # for some reason, running this in the IDE requires me to set the geckodriver path
    with GoogleScholar('/usr/local/bin/geckodriver') as scholar:
        res = scholar.scrape_papers('https://scholar.google.com/citations?user=VGoSakQAAAAJ&hl=en&oi=ao')
        wait()
