import copy
from urllib.parse import urlparse, quote, unquote

from core.arjun import arjun
from core.checker import checker
from core.colors import good, bad, end, info, green, run, red, que
from core.config import xsschecker, minEfficiency
from core.dom import dom
from core.filterChecker import filterChecker
from core.generator import generator
from core.htmlParser import htmlParser
from core.requester import requester
from core.utils import getUrl, getParams, verboseOutput
from core.wafDetector import wafDetector

def scan(target, paramData, verbose, encoding, headers, delay, timeout, skipDOM, find, skip, browser):
    GET, POST = (False, True) if paramData else (True, False)
    # If the user hasn't supplied the root url with http(s), we will handle it
    if not target.startswith('http'):
        try:
            response = requester('https://' + target, {},
                                 headers, GET, delay, timeout)
            target = 'https://' + target
        except:
            target = 'http://' + target
    response = requester(target, {}, headers, GET, delay, timeout).text
    if not skipDOM:
        print('%s Checking for DOM vulnerabilities' % run)
        highlighted = dom(response)
        if highlighted:
            print('%s Potentially vulnerable objects found' % good)
            print(red + ('-' * 60) + end)
            for line in highlighted:
                print(line)
            print(red + ('-' * 60) + end)
    host = urlparse(target).netloc  # Extracts host out of the url
    verboseOutput(host, 'host', verbose)
    url = getUrl(target, GET)
    verboseOutput(url, 'url', verbose)
    params = getParams(target, paramData, GET)
    verboseOutput(params, 'params', verbose)
    if find:
        params = arjun(url, GET, headers, delay, timeout)
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
        paramsCopy = copy.deepcopy(params)
        print('%s Testing parameter: %s' % (info, paramName))
        if encoding:
            paramsCopy[paramName] = encoding(xsschecker)
        else:
            paramsCopy[paramName] = xsschecker
        response = requester(url, paramsCopy, headers, GET, delay, timeout)
        parsedResponse = htmlParser(response, encoding)
        occurences = parsedResponse[0]
        verboseOutput(occurences, 'occurences', verbose)
        positions = parsedResponse[1]
        verboseOutput(positions, 'positions', verbose)
        if not occurences:
            print('%s No reflection found' % bad)
            continue
        else:
            print('%s Reflections found: %s' % (info, len(occurences)))
        print('%s Analysing reflections' % run)
        efficiencies = filterChecker(
            url, paramsCopy, headers, GET, delay, occurences, timeout, encoding)
        verboseOutput(efficiencies, 'efficiencies', verbose)
        print('%s Generating payloads' % run)
        vectors = generator(occurences, response.text)
        verboseOutput(vectors, 'vectors', verbose)
        total = 0
        for v in vectors.values():
            total += len(v)
        if total == 0:
            print('%s No vectors were crafted' % bad)
            continue
        print('%s Payloads generated: %i' % (info, total))
        progress = 0
        for confidence, vects in vectors.items():
            for vect in vects:
                progress += 1
                if not GET:
                    vect = unquote(vect)
                if browser:
                	from core.browserEngine import browserEngine
                	paramsCopy[paramName] = vect
                	response = requester(url, paramsCopy, headers, GET, delay, timeout).text
                	success = browserEngine(browser, response)
                	if success:
                		print('%s Payload: %s' % (good, vect))
                else:
	                efficiencies = checker(
	                    url, paramsCopy, headers, GET, delay, vect, positions, timeout, encoding)
	                if not GET:
	                    vect = quote(vect)
	                if not efficiencies:
	                    for i in range(len(occurences)):
	                        efficiencies.append(0)
	                bestEfficiency = max(efficiencies)
	                if bestEfficiency == 100 or (vect[0] == '\\' and bestEfficiency >= 95):
	                    print(('%s-%s' % (red, end)) * 60)
	                    print('%s Payload: %s' % (good, vect))
	                    print('%s Efficiency: %i' % (info, bestEfficiency))
	                    print('%s Confidence: %i' % (info, confidence))
	                    if not skip:
	                        choice = input(
	                            '%s Would you like to continue scanning? [y/N] ' % que).lower()
	                        if choice != 'y':
	                            quit()
	                elif bestEfficiency > minEfficiency:
	                    print(('%s-%s' % (red, end)) * 60)
	                    print('%s Payload: %s' % (good, vect))
	                    print('%s Efficiency: %i' % (info, bestEfficiency))
	                    print('%s Confidence: %i' % (info, confidence))
