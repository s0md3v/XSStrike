import copy
from urllib.parse import urlparse

from core.colors import bad, green, end, good, info
from core.config import xsschecker
from core.fuzzer import fuzzer
from core.requester import requester
from core.utils import getUrl, getParams, logger
from core.wafDetector import wafDetector

def singleFuzz(target, paramData, encoding, headers, delay, timeout):
    GET, POST = (False, True) if paramData else (True, False)
    # If the user hasn't supplied the root url with http(s), we will handle it
    if not target.startswith('http'):
        try:
            response = requester('https://' + target, {},
                                 headers, GET, delay, timeout)
            target = 'https://' + target
        except:
            target = 'http://' + target
    logger(target, flag='debug', variable='target', function='singleFuzz')
    host = urlparse(target).netloc  # Extracts host out of the url
    logger(host, flag='debug', variable='host', function='singleFuzz')
    url = getUrl(target, GET)
    logger(url, flag='debug', variable='url', function='singleFuzz')
    params = getParams(target, paramData, GET)
    logger(params, flag='debug', variable='params', function='singleFuzz')
    if not params:
        logger('%s No parameters to test.' % bad)
        quit()
    WAF = wafDetector(
        url, {list(params.keys())[0]: xsschecker}, headers, GET, delay, timeout)
    if WAF:
        logger('%s WAF detected: %s%s%s' % (bad, green, WAF, end))
    else:
        logger('%s WAF Status: %sOffline%s' % (good, green, end))

    for paramName in params.keys():
        logger('%s Fuzzing parameter: %s' % (info, paramName))
        paramsCopy = copy.deepcopy(params)
        paramsCopy[paramName] = xsschecker
        fuzzer(url, paramsCopy, headers, GET,
               delay, timeout, WAF, encoding)
