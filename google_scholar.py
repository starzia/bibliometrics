import urllib
import time
from professor import Professor
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium import webdriver

from web_util import wait


class GoogleScholar:
    def __init__(self):
        self.selenium_driver = webdriver.Firefox()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.selenium_driver.quit()

    def find_google_scholar_page(self, prof: Professor):
        """NOTE: google is very proactive about blocking requests if it thinks you are a bot,
        so this sometimes results in a 503 error. """
        wait()
        # get search results page
        self.selenium_driver.get('https://scholar.google.com/scholar?q=author%%3A"%s"+%s' %
                                 (urllib.parse.quote(prof.simple_name()), prof.school))

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

        # scrape the results
        try:
            anchor = self.selenium_driver.find_element_by_css_selector('h4.gs_rt2 a')
            return anchor.get_attribute('href')
        except NoSuchElementException:
            return None