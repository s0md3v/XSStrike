import copy
from urllib.parse import urlparse

from core.colors import bad, green, end, good, info
from core.config import xsschecker
from core.fuzzer import fuzzer
from core.requester import requester
from core.utils import getUrl, getParams, verboseOutput
from core.wafDetector import wafDetector

def singleFuzz(target, paramData, verbose, encoding, headers, delay, timeout):
    GET, POST = (False, True) if paramData else (True, False)
    # If the user hasn't supplied the root url with http(s), we will handle it
    if not target.startswith('http'):
        try:
            response = requester('https://' + target, {},
                                 headers, GET, delay, timeout)
            target = 'https://' + target
        except:
            target = 'http://' + target
    host = urlparse(target).netloc  # Extracts host out of the url
    verboseOutput(host, 'host', verbose)
    url = getUrl(target, GET)
    verboseOutput(url, 'url', verbose)
    params = getParams(target, paramData, GET)
    verboseOutput(params, 'params', verbose)
    if not params:
        print('%s No parameters to test.' % bad)
        quit()
    WAF = wafDetector(
        url, {list(params.keys())[0]: xsschecker}, headers, GET, delay, timeout)
    if WAF:
        print('%s WAF detected: %s%s%s' % (bad, green, WAF, end))
    else:
        print('%s WAF Status: %sOffline%s' % (good, green, end))

    for paramName in params.keys():
        print('%s Fuzzing parameter: %s' % (info, paramName))
        paramsCopy = copy.deepcopy(params)
        paramsCopy[paramName] = xsschecker
        fuzzer(url, paramsCopy, headers, GET,
               delay, timeout, WAF, encoding)
