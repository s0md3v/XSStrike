import copy
import re
from urllib.parse import urlparse, quote, unquote

from core.arjun import arjun
from core.browserEngine import browserEngine
from core.checker import checker
from core.colors import good, bad, end, info, green, run, red, que
import core.config
from core.config import xsschecker, minEfficiency
from core.dom import dom
from core.filterChecker import filterChecker
from core.generator import generator
from core.htmlParser import htmlParser
from core.requester import requester
from core.utils import getUrl, getParams, logger
from core.wafDetector import wafDetector

def scan(target, paramData, encoding, headers, delay, timeout, skipDOM, find, skip):
    GET, POST = (False, True) if paramData else (True, False)
    # If the user hasn't supplied the root url with http(s), we will handle it
    if not target.startswith('http'):
        try:
            response = requester('https://' + target, {},
                                 headers, GET, delay, timeout)
            target = 'https://' + target
        except:
            target = 'http://' + target
    logger(target, flag='debug', variable='target', function='scan')
    response = requester(target, {}, headers, GET, delay, timeout).text
    if not skipDOM:
        logger('%s Checking for DOM vulnerabilities' % run)
        highlighted = dom(response)
        if highlighted:
            logger('%s Potentially vulnerable objects found' % good)
            logger(red + ('-' * 60) + end)
            for line in highlighted:
                logger(line)
            logger(red + ('-' * 60) + end)
    host = urlparse(target).netloc  # Extracts host out of the url
    logger(host, flag='debug', variable='host', function='scan')
    url = getUrl(target, GET)
    logger(url, flag='debug', variable='url', function='scan')
    params = getParams(target, paramData, GET)
    logger(logger, flag='debug', variable='logger', function='scan')
    if find:
        params = arjun(url, GET, headers, delay, timeout)
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
        paramsCopy = copy.deepcopy(params)
        logger('%s Testing parameter: %s' % (info, paramName))
        if encoding:
            paramsCopy[paramName] = encoding(xsschecker)
        else:
            paramsCopy[paramName] = xsschecker
        response = requester(url, paramsCopy, headers, GET, delay, timeout)
        parsedResponse = htmlParser(response, encoding)
        occurences = parsedResponse[0]
        logger(occurences, 'occurences')
        positions = parsedResponse[1]
        logger(positions, 'positions')
        if not occurences:
            logger('%s No reflection found' % bad)
            continue
        else:
            logger('%s Reflections found: %s' % (info, len(occurences)))
        logger('%s Analysing reflections' % run)
        efficiencies = filterChecker(
            url, paramsCopy, headers, GET, delay, occurences, timeout, encoding)
        logger(efficiencies, flag='debug', variable='efficiencies', function='scan')
        logger('%s Generating payloads' % run)
        vectors = generator(occurences, response.text)
        logger(vectors, flag='debug', variable='vectors', function='scan')
        total = 0
        for v in vectors.values():
            total += len(v)
        if total == 0:
            logger('%s No vectors were crafted' % bad)
            continue
        logger('%s Payloads generated: %i' % (info, total))
        progress = 0
        for confidence, vects in vectors.items():
            for vect in vects:
                if core.config.globalVariables['path']:
                    vect = vect.replace('/', '%2F')
                loggerVector = vect
                progress += 1
                print('%s Progress: %i/%i' % (run, progress, total), end='\r')
                if confidence == 10:
                    if not GET:
                        vect = unquote(vect)
                    efficiencies = checker(
                        url, paramsCopy, headers, GET, delay, vect, positions, timeout, encoding)
                    if not efficiencies:
                        for i in range(len(occurences)):
                            efficiencies.append(0)
                    bestEfficiency = max(efficiencies)
                    if bestEfficiency == 100 or (vect[0] == '\\' and bestEfficiency >= 95):
                        logger(('%s-%s' % (red, end)) * 60)
                        logger('%s Payload: %s' % (good, loggerVector))
                        logger('%s Efficiency: %i' % (info, bestEfficiency))
                        logger('%s Confidence: %i' % (info, confidence))
                        if not skip:
                            choice = input(
                                '%s Would you like to continue scanning? [y/N] ' % que).lower()
                            if choice != 'y':
                                quit()
                    elif bestEfficiency > minEfficiency:
                        logger(('%s-%s' % (red, end)) * 60)
                        logger('%s Payload: %s' % (good, loggerVector))
                        logger('%s Efficiency: %i' % (info, bestEfficiency))
                        logger('%s Confidence: %i' % (info, confidence))
                else:
                    if re.search(r'<(a|d3|details)|lt;(a|d3|details)', vect.lower()):
                        continue
                    vect = unquote(vect)
                    if encoding:
                        paramsCopy[paramName] = encoding(vect)
                    else:
                        paramsCopy[paramName] = vect
                    response = requester(url, paramsCopy, headers, GET, delay, timeout).text
                    success = browserEngine(response)
                    if success:
                        logger(('%s-%s' % (red, end)) * 60)
                        logger('%s Payload: %s' % (good, loggerVector))
                        logger('%s Efficiency: %i' % (info, 100))
                        logger('%s Confidence: %i' % (info, 10))
                        if not skip:
                            choice = input(
                                '%s Would you like to continue scanning? [y/N] ' % que).lower()
                            if choice != 'y':
                                quit()
        logger('')
