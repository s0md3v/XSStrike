import copy
import re

from core.colors import red, good, green, end
from core.config import xsschecker
from core.dom import dom
from core.filterChecker import filterChecker
from core.generator import generator
from core.htmlParser import htmlParser
from core.requester import requester
from core.log import setup_logger

logger = setup_logger(__name__)


def crawl(scheme, host, main_url, form, domURL, blindXSS, blindPayload, headers, delay, timeout, skipDOM, encoding):
    if domURL and not skipDOM:
        response = requester(domURL, {}, headers, True, delay, timeout).text
        highlighted = dom(response)
        if highlighted:
            logger.good('Potentially vulnerable objects found at %s' % domURL)
            logger.red_line(level='good')
            for line in highlighted:
                logger.no_format(line, level='good')
            logger.red_line(level='good')
    if form:
        for each in form.values():
            url = each['action']
            if url:
                if url.startswith(main_url):
                    pass
                elif url.startswith('//') and url[2:].startswith(host):
                    url = scheme + '://' + url[2:]
                elif url.startswith('/'):
                    url = scheme + '://' + host + url
                elif re.match(r'\w', url[0]):
                    url = scheme + '://' + host + '/' + url
                method = each['method']
                GET = True if method == 'get' else False
                inputs = each['inputs']
                paramData = {}
                for one in inputs:
                    paramData[one['name']] = one['value']
                    for paramName in paramData.keys():
                        paramsCopy = copy.deepcopy(paramData)
                        paramsCopy[paramName] = xsschecker
                        response = requester(
                            url, paramsCopy, headers, GET, delay, timeout)
                        parsedResponse = htmlParser(response, encoding)
                        occurences = parsedResponse[0]
                        positions = parsedResponse[1]
                        efficiencies = filterChecker(
                            url, paramsCopy, headers, GET, delay, occurences, timeout, encoding)
                        vectors = generator(occurences, response.text)
                        if vectors:
                            for confidence, vects in vectors.items():
                                try:
                                    payload = list(vects)[0]
                                    logger.vuln('Vulnerable webpage: %s%s%s' %
                                                (green, url, end))
                                    logger.vuln('Vector for %s%s%s: %s' %
                                                (green, paramName, end, payload))
                                    break
                                except IndexError:
                                    pass
                        if blindXSS and blindPayload:
                            paramsCopy[paramName] = blindPayload
                            requester(url, paramsCopy, headers,
                                      GET, delay, timeout)
