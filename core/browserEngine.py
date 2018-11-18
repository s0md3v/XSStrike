import re
import os
import sys
from core.utils import writer, reader
from selenium.common.exceptions import UnexpectedAlertPresentException

def browserEngine(browser, response):
    # os.remove(sys.path[0] + '/test.html')
    # print ('writing')
    # writer(response, sys.path[0] + '/test.html')
    print ('opening: ' + 'file://' + sys.path[0] + '/test.html')
    browser.get('data:text/html,' + response)
    print ('next')
    popUp = False
    try:
        browser.close()
    except UnexpectedAlertPresentException:
        popUp = True
    browser.quit()
    print ('donnnnnnne', popUp)
    return popUp