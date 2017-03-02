import urllib
import time
from professor import Professor
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, InvalidElementStateException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium import webdriver

from web_util import wait, tree_from_string, css_select, Selector
from typing import List


def empty_to_none(string):
    return string if len(string) > 0 else None

class Paper:
    def __init__(self, title, authors, venue, year, citation_count):
        self.title = title
        self.authors = authors
        self.venue = venue
        self.year = year
        self.citation_count = citation_count


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
        """NOTE: google is very proactive about blocking requests if it thinks you are a bot,
        so this sometimes results in a 503 error. """
        wait()
        # get search results page
        self.selenium_driver.get('https://scholar.google.com/scholar?q=author%%3A"%s"+%s' %
                                 (urllib.parse.quote(prof.simple_name()), prof.school))
        self.wait_for_captchas()
        # scrape the results
        try:
            anchor = self.selenium_driver.find_element_by_css_selector('h4.gs_rt2 a')
            return anchor.get_attribute('href')
        except NoSuchElementException:
            return None

    # eg., see https://scholar.google.com/citations?user=VGoSakQAAAAJ&hl=en&oi=ao
    def scrape_papers(self, author_url) -> List[Paper]:
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
            author = empty_to_none(authors_and_venue[0].text)
            venue = empty_to_none(authors_and_venue[1].text)
            year = empty_to_none(Selector('td.gsc_a_y')(row))
            citation_count = empty_to_none(Selector('td.gsc_a_c a.gsc_a_ac')(row))
            # look for strikeout (cross-out) over citation count, indicating that it's a dupe
            if Selector('td.gsc_a_c a.gsc_a_acm')(row):
                continue
            papers.append(Paper(title, author, venue, year, citation_count))
        return papers


if __name__ == '__main__':
    # for some reason, running this in the IDE requires me to set the geckodriver path
    with GoogleScholar('/usr/local/bin/geckodriver') as scholar:
        res = scholar.scrape_papers('https://scholar.google.com/citations?user=VGoSakQAAAAJ&hl=en&oi=ao')
        wait()
