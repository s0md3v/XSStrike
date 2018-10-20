import re
import random
from core.config import xsschecker

def replacer(dic, toReplace, replaceWith):
    for key in dic.keys():
        if dic[key] == toReplace:
            dic[key] = replaceWith
    return dic

def getUrl(url, data, GET):
    if GET:
        return url.split('?')[0]
    else:
        return url

def extractScripts(response):
    scripts = []
    matches = re.findall(r'(?s)<script.*?>(.*?)</script>', response.lower())
    for match in matches:
        if xsschecker in match:
            scripts.append(match)
    return scripts

def randomUpper(string):
    return ''.join(random.choice((x, y)) for x, y in zip(string.upper(),string.lower()))

def flattenParams(currentParam, params, payload):
    flatted = []
    for name, value in params.items():
        if name == currentParam:
            value = payload
        flatted.append(name + '=' + value)
    return '?' + '&'.join(flatted)

def genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, breaker, special):
    vectors = []
    r = randomUpper
    for tag in tags:
        if tag == 'd3v' or tag == 'a':
            bait = 'z'
        else:
            bait = ''
        for eventHandler in eventHandlers:
            if tag in eventHandlers[eventHandler]:
                for function in functions:
                    for filling in fillings:
                        for eFilling in eFillings:
                            for lFilling in lFillings:
                                for end in ends:
                                    if tag == 'd3v' or tag == 'a':
                                        if '>' in ends:
                                            end = '>'
                                    vector = vector = r(breaker) + special + '<' + r(tag) + filling + r(eventHandler) + eFilling + '=' + eFilling + function + lFilling + end + bait
                                    vectors.append(vector)
    return vectors

def getParams(url, data, GET):
    params = {}
    if GET:
        if '=' in url:
            data = url.split('?')[1]
            if data[:1] == '?':
                data = data[1:]
        else:
            data = ''
    parts = data.split('&')
    for part in parts:
        each = part.split('=')
        try:
            params[each[0]] = each[1]
        except IndexError:
            params = None
    return params