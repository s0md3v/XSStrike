import re
import os
import sys

from core.log import setup_logger
from core.utils import writer
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.support import expected_conditions as EC


def init_browser():
    global browser
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)


def kill_browser():
    if browser is not None:
        browser.quit()


def browser_engine(response):
    _write_response_to_file(response)
    navigate_to('file://' + sys.path[0] + '/test.html')
    os.remove('test.html')
    popUp = False
    actions = webdriver.ActionChains(browser)

    try:
        actions.move_by_offset(2, 2)
        actions.perform()
        if EC.alert_is_present():
            popUp = True

    except UnexpectedAlertPresentException:
        popUp = True

    return popUp


def _write_response_to_file(response):
    response = re.sub(r'<script.*?src=.*?>', '<script src=#>', response, re.I)
    response = re.sub(r'href=.*?>', 'href=#>', response, re.I)
    writer(response, 'test.html')


def navigate_to(uri):
    if browser is None:
        init_browser()
        browser.get(uri)



