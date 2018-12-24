import concurrent.futures
import re

from core.colors import good, info, green, end
from core.config import blindParams, xsschecker, threadCount
from core.requester import requester


def checky(param, paraNames, url, headers, GET, delay, timeout):
    if param not in paraNames:
        response = requester(url, {param: xsschecker},
                             headers, GET, delay, timeout).text
        if '\'%s\'' % xsschecker in response or '"%s"' % xsschecker in response or ' %s ' % xsschecker in response:
            paraNames[param] = ''
            print('%s Valid parameter found : %s%s%s' %
                  (good, green, param, end))


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
        print('%s Heuristics found a potentially valid parameter: %s%s%s. Priortizing it.' % (
            good, green, foundParam, end))
        if foundParam not in blindParams:
            blindParams.insert(0, foundParam)
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
    futures = (threadpool.submit(checky, param, paraNames, url,
                                 headers, GET, delay, timeout) for param in blindParams)
    for i, _ in enumerate(concurrent.futures.as_completed(futures)):
        if i + 1 == len(blindParams) or (i + 1) % threadCount == 0:
            print('%s Progress: %i/%i' % (info, i + 1, len(blindParams)), end='\r')
    return paraNames
