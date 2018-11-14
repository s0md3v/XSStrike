#!/usr/bin/env python3

from __future__ import print_function

from core.colors import end, red, white, green, yellow, run, bad, good, info, que

# Just a fancy ass banner
print('''%s
\tXSStrike %sv3.0.2
%s''' % (red, white, end))

try:
    from urllib.parse import quote_plus, unquote, urlparse
except ImportError: # throws error in python2
    print ('%s XSStrike isn\'t compatible with python2.\n Use python > 3.4 to run XSStrike.' % bad)
    quit()

# Let's import whatever we need
import re
import os
import sys
import copy
import argparse
import requests
import concurrent.futures

import core.config
from core.dom import dom
from core.arjun import arjun
from core.photon import photon
from core.prompt import prompt
from core.fuzzer import fuzzer
from core.updater import updater
from core.checker import checker
from core.encoders import base64
from core.generator import generator
from core.requester import requester
from core.htmlParser import htmlParser
from core.wafDetector import wafDetector
from core.filterChecker import filterChecker
from core.config import xsschecker, minEfficiency, blindPayload
from core.utils import getUrl, getParams, flattenParams, extractHeaders, verboseOutput

# Processing command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', help='url', dest='target')
parser.add_argument('--data', help='post data', dest='data')
parser.add_argument('-e', '--encode', help='encode payloads', dest='encode')
parser.add_argument('--fuzzer', help='fuzzer', dest='fuzz', action='store_true')
parser.add_argument('--update', help='update', dest='update', action='store_true')
parser.add_argument('--timeout', help='timeout', dest='timeout', type=int)
parser.add_argument('--proxy', help='use prox(y|ies)', dest='proxy', action='store_true')
parser.add_argument('--params', help='find params', dest='find', action='store_true')
parser.add_argument('--crawl', help='crawl', dest='recursive', action='store_true')
parser.add_argument('-f', '--file', help='load payloads from a file', dest='file')
parser.add_argument('-l', '--level', help='level of crawling', dest='level', type=int)
parser.add_argument('--headers', help='add headers', dest='headers', action='store_true')
parser.add_argument('-t', '--threads', help='number of threads', dest='threads', type=int)
parser.add_argument('-d', '--delay', help='delay between requests', dest='delay', type=int)
parser.add_argument('--skip', help='don\'t ask to continue', dest='skip', action='store_true')
parser.add_argument('--skip-dom', help='skip dom checking', dest='skipDOM', action='store_true')
parser.add_argument('-v', '--vectors', help='verbose output', dest='verbose', action='store_true')
parser.add_argument('--blind', help='inject blind XSS payload while crawling', dest='blindXSS', action='store_true')
args = parser.parse_args()

if args.headers:
    headers = extractHeaders(prompt())
else:
    from core.config import headers

find = args.find
fuzz = args.fuzz
encode = args.encode
target = args.target
paramData = args.data
verbose = args.verbose
skipDOM = args.skipDOM
level = args.level or 2
blindXSS = args.blindXSS
delay = args.delay or core.config.delay
timeout = args.timeout or core.config.timeout
threadCount = args.threads or core.config.threadCount

if args.file:
    if args.file == 'default':
        payloadList = core.config.payloads
    else:
        payloadList = []
        with open(args.file, 'r') as f:
            for line in f:
                payloadList.append(line.rstrip('\n'))

encoding = False
if encode:
    if encode == 'base64':
        encoding = base64

if not args.proxy:
    core.config.proxies = {}

if args.update: # if the user has supplied --update argument
    updater()
    quit() # quitting because files have been changed

if not target: # if the user hasn't supplied a url
    print('\n' + parser.format_help().lower())
    quit()

def singleTarget(target, paramData, verbose, encoding):
    if paramData:
        GET, POST = False, True
    else:
        GET, POST = True, False
    # If the user hasn't supplied the root url with http(s), we will handle it
    if target.startswith('http'):
        target = target
    else:
        try:
            response = requester('https://' + target, {}, headers, GET, delay, timeout)
            target = 'https://' + target
        except:
            target = 'http://' + target
    response = requester(target, {}, headers, GET, delay, timeout).text
    if not skipDOM:
        print ('%s Checking for DOM vulnerabilities' % run)
        highlighted = dom(response)
        if highlighted:
            print ('%s Potentially vulnerable objects found' % good)
            print (red + ('-' * 60) + end)
            for line in highlighted:
                print (line)
            print (red + ('-' * 60) + end)
    host = urlparse(target).netloc # Extracts host out of the url
    verboseOutput(host, 'host', verbose)
    url = getUrl(target, GET)
    verboseOutput(url, 'url', verbose)
    params = getParams(target, paramData, GET)
    verboseOutput(params, 'params', verbose)
    if args.find:
        params = arjun(url, GET, headers, delay, timeout)
    if not params:
        quit()
    WAF = wafDetector(url, {list(params.keys())[0] : xsschecker}, headers, GET, delay, timeout)
    if WAF:
        print ('%s WAF detected: %s%s%s' % (bad, green, WAF, end))
    else:
        print ('%s WAF Status: %sOffline%s' % (good, green, end))

    if fuzz:
        for paramName in params.keys():
            print ('%s Fuzzing parameter: %s' % (info, paramName))
            paramsCopy = copy.deepcopy(params)
            paramsCopy[paramName] = xsschecker
            fuzzer(url, paramsCopy, headers, GET, delay, timeout, WAF, encoding)
        quit()

    for paramName in params.keys():
        paramsCopy = copy.deepcopy(params)
        print ('%s Testing parameter: %s' % (info, paramName))
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
            print ('%s No reflection found' % bad)
            continue
        else:
            print ('%s Reflections found: %s' % (info, len(occurences)))
        print ('%s Analysing reflections' % run)
        efficiencies = filterChecker(url, paramsCopy, headers, GET, delay, occurences, timeout, encoding)
        verboseOutput(efficiencies, 'efficiencies', verbose)
        print ('%s Generating payloads' % run)
        vectors = generator(occurences, response.text)
        verboseOutput(vectors, 'vectors', verbose)
        total = 0
        for v in vectors.values():
            total += len(v)
        if total == 0:
            print ('%s No vectors were crafted' % bad)
            continue
        print ('%s Payloads generated: %i' % (info, total))
        progress = 0
        for confidence, vects in vectors.items():
            for vect in vects:
                progress += 1
                print ('%s Payloads tried [%i/%i]' % (run, progress, total), end='\r')
                if not GET:
                    vect = unquote(vect)
                efficiencies = checker(url, paramsCopy, headers, GET, delay, vect, positions, timeout, encoding)
                if not efficiencies:
                    for i in range(len(occurences)):
                        efficiencies.append(0)
                bestEfficiency = max(efficiencies)
                if bestEfficiency == 100 or (vect[0] == '\\' and bestEfficiency >= 95):
                    print (('%s-%s' % (red, end)) * 60)
                    print ('%s Payload: %s' % (good, vect))
                    print ('%s Efficiency: %i' % (info, bestEfficiency))
                    print ('%s Confidence: %i' % (info, confidence))
                    if not args.skip:
                        choice = input('%s Would you like to continue scanning? [y/N] ' % que).lower()
                        if choice != 'y':
                            quit()
                elif bestEfficiency > minEfficiency:
                    print (('%s-%s' % (red, end)) * 60)
                    print ('%s Payload: %s' % (good, vect))
                    print ('%s Efficiency: %i' % (info, bestEfficiency))
                    print ('%s Confidence: %i' % (info, confidence))

def multiTargets(scheme, host, main_url, form, domURL, verbose, blindXSS, blindPayload):
    signatures = set()
    if domURL and not skipDOM:
        response = requests.get(domURL).text
        highlighted = dom(response)
        if highlighted:
            print ('%s Potentially vulnerable objects found at %s' % (good, domURL))
            print (red + ('-' * 60) + end)
            for line in highlighted:
                print (line)
            print (red + ('-' * 60) + end)
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
                if method == 'get':
                    GET = True
                else:
                    GET = False
                inputs = each['inputs']
                paramData = {}
                for one in inputs:
                    paramData[one['name']] = one['value']
                    for paramName in paramData.keys():
                        paramsCopy = copy.deepcopy(paramData)
                        paramsCopy[paramName] = xsschecker
                        response = requester(url, paramsCopy, headers, GET, delay, timeout)
                        parsedResponse = htmlParser(response, encoding)
                        occurences = parsedResponse[0]
                        positions = parsedResponse[1]
                        efficiencies = filterChecker(url, paramsCopy, headers, GET, delay, occurences, timeout, encoding)
                        vectors = generator(occurences, response.text)
                        if vectors:
                            for confidence, vects in vectors.items():
                                try:
                                    payload = list(vects)[0]
                                    print ('%s Vulnerable webpage: %s%s%s' % (good, green, url, end))
                                    print ('%s Vector for %s%s%s: %s' % (good, green, paramName, end, payload))
                                    break
                                except IndexError:
                                    pass
                        if blindXSS and blindPayload:
                            paramsCopy[paramName] = blindPayload
                            requester(url, paramsCopy, headers, GET, delay, timeout)


def bruteforcer(target, paramData, payloadList, verbose, encoding):
    if paramData:
        GET, POST = False, True
    else:
        GET, POST = True, False
    host = urlparse(target).netloc # Extracts host out of the url
    verboseOutput(host, 'host', verbose)
    url = getUrl(target, GET)
    verboseOutput(url, 'url', verbose)
    params = getParams(target, paramData, GET)
    verboseOutput(params, 'params', verbose)
    for paramName in params.keys():
        paramsCopy = copy.deepcopy(params)
        for payload in payloadList:
            if encoding:
                payload = encoding(unquote(payload))
            paramsCopy[paramName] = payload
            response = requester(url, paramsCopy, headers, GET, delay, timeout).text
            if encoding:
                payload = encoding(payload)
            if payload in response:
                print ('%s %s' % (good, payload))

if not args.recursive:
    if args.file:
        bruteforcer(target, paramData, payloadList, verbose, encoding)
    else:
        singleTarget(target, paramData, verbose, encoding)
else:
    print ('%s Crawling the target' % run)
    scheme = urlparse(target).scheme
    verboseOutput(scheme, 'scheme', verbose)
    host = urlparse(target).netloc
    main_url = scheme + '://' + host
    crawlingResult = photon(target, headers, level, threadCount, delay, timeout)
    forms = crawlingResult[0]
    domURLs = list(crawlingResult[1])
    difference = abs(len(domURLs) - len(forms))
    if len(domURLs) > len(forms):
        for i in range(difference):
            forms.append(0)
    elif len(forms) > len(domURLs):
        for i in range(difference):
            domURLs.append(0)
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
    futures = (threadpool.submit(multiTargets, scheme, host, main_url, form, domURL, verbose, blindXSS, blindPayload) for form, domURL in zip(forms, domURLs))
    for i, _ in enumerate(concurrent.futures.as_completed(futures)):
        if i + 1 == len(forms) or (i + 1) % threadCount == 0:
            print('%s Progress: %i/%i' % (info, i + 1, len(forms)), end='\r')
    print ('')
