import re
import os
import sys

from core.utils import writer
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException


def init_browser():
    global browser
    options = Options()
    # options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)


def kill_browser():
    global browser
    if browser is not None:
        browser.quit()


def is_alert_present():
    global browser
    try:
        print(browser.switch_to.alert.text)
        browser.switch_to.alert.dismiss()
        return True
    except NoAlertPresentException:
        return False
    except UnexpectedAlertPresentException:
        return True
    except Exception as e:
        print(e)


def browser_engine(response):
    global browser
    _write_response_to_file(response)
    navigate_to('file://' + sys.path[0] + '/test.html')
    os.remove('test.html')
    popUp = False
    actions = webdriver.ActionChains(browser)

    try:
        actions.move_by_offset(2, 2)
        actions.move_by_offset(-2, -2)
        actions.perform()
        if is_alert_present():
            popUp = True

    except UnexpectedAlertPresentException:
        popUp = True
    except Exception as e:
        print(e)
    return popUp


def _write_response_to_file(response):
    response = re.sub(r'<script.*?src=.*?>', '<script src=#>', response, re.I)
    response = re.sub(r'href=.*?>', 'href=#>', response, re.I)
    writer(response, 'test.html')


def navigate_to(uri):
    global browser
    if browser is None:
        init_browser()
    browser.get(uri)
