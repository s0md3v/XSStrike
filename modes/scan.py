from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import re
from threading import Lock
from urllib.parse import urlparse, quote, unquote

from core.checker import checker
from core.colors import end, green, que
import core.config
from core.config import xsschecker, minEfficiency
from core.dom import dom
from core.filterChecker import filterChecker
from core.generator import generator
from core.htmlParser import htmlParser
from core.requester import requester
from core.utils import getUrl, getParams, getVar
from core.wafDetector import wafDetector
from core.log import setup_logger

logger = setup_logger(__name__)
lock = Lock()


def scan(target, paramData, encoding, headers, delay, timeout, skipDOM, skip, threadCount):
    GET, POST = (False, True) if paramData else (True, False)
    # If the user hasn't supplied the root url with http(s), we will handle it
    if not target.startswith('http'):
        try:
            response = requester('https://' + target, {},
                                 headers, GET, delay, timeout)
            target = 'https://' + target
        except:
            target = 'http://' + target
    logger.debug('Scan target: {}'.format(target))
    response = requester(target, {}, headers, GET, delay, timeout).text

    if not skipDOM:
        logger.run('Checking for DOM vulnerabilities')
        highlighted = dom(response)
        if highlighted:
            logger.good('Potentially vulnerable objects found')
            logger.red_line(level='good')
            for line in highlighted:
                logger.no_format(line, level='good')
            logger.red_line(level='good')
    host = urlparse(target).netloc  # Extracts host out of the url
    logger.debug('Host to scan: {}'.format(host))
    url = getUrl(target, GET)
    logger.debug('Url to scan: {}'.format(url))
    params = getParams(target, paramData, GET)
    logger.debug_json('Scan parameters:', params)
    if not params:
        logger.error('No parameters to test.')
        quit()
    WAF = wafDetector(
        url, {list(params.keys())[0]: xsschecker}, headers, GET, delay, timeout)
    if WAF:
        logger.error('WAF detected: %s%s%s' % (green, WAF, end))
    else:
        logger.good('WAF Status: %sOffline%s' % (green, end))

    for paramName in params.keys():
        paramsCopy = copy.deepcopy(params)
        logger.info('Testing parameter: %s' % paramName)
        if encoding:
            paramsCopy[paramName] = encoding(xsschecker)
        else:
            paramsCopy[paramName] = xsschecker
        response = requester(url, paramsCopy, headers, GET, delay, timeout)
        occurences = htmlParser(response, encoding)
        positions = occurences.keys()
        logger.debug('Scan occurences: {}'.format(occurences))
        if not occurences:
            logger.error('No reflection found')
            continue
        else:
            logger.info('Reflections found: %i' % len(occurences))

        logger.run('Analysing reflections')
        efficiencies = filterChecker(
            url, paramsCopy, headers, GET, delay, occurences, timeout, encoding)
        logger.debug('Scan efficiencies: {}'.format(efficiencies))
        logger.run('Generating payloads')
        vectors = generator(occurences, response.text)
        total = 0
        for v in vectors.values():
            total += len(v)
        if total == 0:
            logger.error('No vectors were crafted.')
            continue
        logger.info('Payloads generated: %i' % total)
        progress = {'lap': 0}
        running_futures = []
        with ThreadPoolExecutor(max_workers=threadCount) as executor:

            #  Add all comb
            for confidence, vects in vectors.items():
                for vect in vects:
                    running_futures.append(executor.submit(checky, target, url, paramsCopy, headers, GET, delay,
        vect, positions, timeout, encoding, occurences, confidence, progress, total))
            
            for future in as_completed(running_futures):
                
                # retrieve the result
                bestEfficiency, target, loggerVector, confidence = future.result()

                if bestEfficiency == 100 or (vect[0] == '\\' and bestEfficiency >= 95):
                    lock.acquire()
                    logger.red_line()
                    logger.good('Payload: %s' % loggerVector)
                    logger.info('Efficiency: %i' % bestEfficiency)
                    logger.info('Confidence: %i' % confidence)
                    if not skip:
                        choice = input(
                            '%s Would you like to continue scanning? [y/N] ' % que).lower()
                    lock.release()
                    if skip or choice != 'y':
                        [f.cancel() for f in running_futures]
                        return target, loggerVector                       
                elif bestEfficiency > minEfficiency:
                    lock.acquire()
                    logger.red_line()
                    logger.good('Payload: %s' % loggerVector)
                    logger.info('Efficiency: %i' % bestEfficiency)
                    logger.info('Confidence: %i' % confidence)
                    lock.release()
                    
        logger.no_format('')


def checky(
    target, url, paramsCopy, headers, GET, delay,
        vect, positions, timeout, encoding, occurences, confidence, progress, total):
    if core.config.globalVariables['path']:
        vect = vect.replace('/', '%2F')
    loggerVector = vect
    progress['lap'] += 1
    lock.acquire()
    logger.run(f'Progress: {progress["lap"]}/{total}                                      \r')
    lock.release()
    if not GET:
        vect = unquote(vect)
    efficiencies = checker(
        url, paramsCopy, headers, GET, delay, vect, positions, timeout, encoding)
    if not efficiencies:
        for i in range(len(occurences)):
            efficiencies.append(0)
    bestEfficiency = max(efficiencies)
    return bestEfficiency, target, loggerVector, confidence
