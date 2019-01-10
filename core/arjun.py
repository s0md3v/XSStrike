import concurrent.futures
import re

from core.colors import green, end
from core.config import blindParams, xsschecker, threadCount
from core.requester import requester
from core.log import setup_logger

logger = setup_logger(__name__)


def checky(param, paraNames, url, headers, GET, delay, timeout):
    if param not in paraNames:
        logger.debug('Checking param: {}'.format(param))
        response = requester(url, {param: xsschecker},
                             headers, GET, delay, timeout).text
        if '\'%s\'' % xsschecker in response or '"%s"' % xsschecker in response or ' %s ' % xsschecker in response:
            paraNames[param] = ''
            logger.good('Valid parameter found: %s%s', green, param)


def arjun(url, GET, headers, delay, timeout):
    paraNames = {}
    response = requester(url, {}, headers, GET, delay, timeout).text
    matches = re.findall(
        r'<input.*?name=\'(.*?)\'.*?>|<input.*?name="(.*?)".*?>', response)
    for match in matches:
        try:
            foundParam = match[1]
        except UnicodeDecodeError:
            continue
        logger.good('Heuristics found a potentially valid parameter: %s%s%s. Priortizing it.' % (
            green, foundParam, end))
        if foundParam not in blindParams:
            blindParams.insert(0, foundParam)
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
    futures = (threadpool.submit(checky, param, paraNames, url,
                                 headers, GET, delay, timeout) for param in blindParams)
    for i, _ in enumerate(concurrent.futures.as_completed(futures)):
        if i + 1 == len(blindParams) or (i + 1) % threadCount == 0:
            logger.info('Progress: %i/%i\r' % (i + 1, len(blindParams)))
    return paraNames
