import copy
from urllib.parse import urlparse, unquote

from core.colors import run, good, bad, green, end
from core.requester import requester
from core.utils import getUrl, getParams, verboseOutput
from core.log import setup_logger

logger = setup_logger(__name__)

def bruteforcer(target, paramData, payloadList, verbose, encoding, headers, delay, timeout):
    GET, POST = (False, True) if paramData else (True, False)
    host = urlparse(target).netloc  # Extracts host out of the url
    verboseOutput(host, 'host', verbose)
    url = getUrl(target, GET)
    verboseOutput(url, 'url', verbose)
    params = getParams(target, paramData, GET)
    if not params:
        logger.error('No parameters to test.')
        quit()
    verboseOutput(params, 'params', verbose)
    for paramName in params.keys():
        progress = 1
        paramsCopy = copy.deepcopy(params)
        for payload in payloadList:
            print ('%s Bruteforcing %s[%s%s%s]%s: %i/%i' % (run, green, end, paramName, green, end, progress, len(payloadList)), end='\r')
            if encoding:
                payload = encoding(unquote(payload))
            paramsCopy[paramName] = payload
            response = requester(url, paramsCopy, headers,
                                 GET, delay, timeout).text
            if encoding:
                payload = encoding(payload)
            if payload in response:
                logger.info('%s %s' % (good, payload))
            progress += 1
    print ()
