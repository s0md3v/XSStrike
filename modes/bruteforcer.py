import copy
from urllib.parse import urlparse, unquote

from core.colors import run, good, bad, green, end
from core.requester import requester
from core.utils import getUrl, getParams, logger

def bruteforcer(target, paramData, payloadList, verbose, encoding, headers, delay, timeout):
    GET, POST = (False, True) if paramData else (True, False)
    host = urlparse(target).netloc  # Extracts host out of the url
    logger(host, flag='debug', variable='host', function='bruteforcer')
    url = getUrl(target, GET)
    logger(url, flag='debug', variable='url', function='bruteforcer')
    params = getParams(target, paramData, GET)
    logger(params, flag='debug', variable='params', function='bruteforcer')
    if not params:
        logger('%s No parameters to test.' % bad)
        quit()
    logger(params, 'params', verbose)
    for paramName in params.keys():
        progress = 1
        paramsCopy = copy.deepcopy(params)
        for payload in payloadList:
            print('%s Bruteforcing %s[%s%s%s]%s: %i/%i' % (run, green, end, paramName, green, end, progress, len(payloadList)), end='\r')
            if encoding:
                payload = encoding(unquote(payload))
            paramsCopy[paramName] = payload
            response = requester(url, paramsCopy, headers,
                                 GET, delay, timeout).text
            if encoding:
                payload = encoding(payload)
            if payload in response:
                logger('%s %s' % (good, payload))
            progress += 1
    logger('')
