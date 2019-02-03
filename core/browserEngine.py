import re
import os
import sys
from core.utils import writer
from core.log import setup_logger
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException, WebDriverException

logger = setup_logger(__name__)


def browserEngine(response):
    options = Options()
    options.add_argument('--headless')
    try:
        browser = webdriver.Firefox(options=options)
    except WebDriverException as e:
        logger.error('There was an error initializing selenium web driver: {}'.format(str(e).strip('Message: ').strip()))
        return e
    response = re.sub(r'<script.*?src=.*?>', '<script src=#>', response, re.I)
    response = re.sub(r'href=.*?>', 'href=#>', response, re.I)
    writer(response, 'test.html')
    browser.get('file://' + sys.path[0] + '/test.html')
    os.remove('test.html')
    popUp = False
    actions = webdriver.ActionChains(browser)
    try:
        actions.move_by_offset(2, 2)
        actions.perform()
        browser.close()
    except UnexpectedAlertPresentException:
        popUp = True
        browser.quit()
    return popUp
