from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
from threading import Lock
from urllib.parse import urlparse, unquote

from core.colors import good, green, end
from core.requester import requester
from core.utils import getUrl, getParams
from core.log import setup_logger

logger = setup_logger(__name__)
lock = Lock()


def bruteforcer(target, paramData, payloadList, encoding, headers, delay, timeout, threadCount):
    GET, POST = (False, True) if paramData else (True, False)
    host = urlparse(target).netloc  # Extracts host out of the url
    logger.debug('Parsed host to bruteforce: {}'.format(host))
    url = getUrl(target, GET)
    logger.debug('Parsed url to bruteforce: {}'.format(url))
    params = getParams(target, paramData, GET)
    logger.debug_json('Bruteforcer params:', params)
    if not params:
        logger.error('No parameters to test.')
        quit()
    progress = {'lap': 0}
    with ThreadPoolExecutor(max_workers=threadCount) as executor:
        
        for paramName in params.keys():
            paramsCopy = copy.deepcopy(params)
            for payload in payloadList:
                executor.submit(
                    make_request, url, payload, paramsCopy, headers, GET,
                        delay, timeout, paramName, encoding, progress, len(payloadList))
    logger.no_format('')


def make_request(url, payload, paramsCopy, headers, GET, delay, timeout, paramName, encoding, progress, total):
    logger.run('Bruteforcing %s[%s%s%s]%s: %i/%i                                       \r' %
            (green, end, paramName, green, end,  progress['lap'], total))
    if encoding:
        payload = encoding(unquote(payload))
    paramsCopy[paramName] = payload
    response = requester(url, paramsCopy, headers,
                        GET, delay, timeout).text
    if encoding:
        payload = encoding(payload)
    if payload in response:
        li = response.split(payload)
        if li[0][-1] != '"' and li[1][0] != '"':
            logger.good(payload)
    progress['lap'] += 1