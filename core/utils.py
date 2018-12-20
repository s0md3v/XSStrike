import json
import random
import re
from urllib.parse import urlparse

import core.config
from core.colors import info, red, end
from core.config import xsschecker

def converter(data, url=False):
    if 'str' in str(type(data)):
        if url:
            dictized = {}
            parts = data.split('/')[3:]
            for part in parts:
                dictized[part] = part
            return dictized
        else:
            return json.loads(data)
    else:
        if url:
            url = urlparse(url).scheme + '://' + urlparse(url).netloc
            for part in list(data.values()):
                url += '/' + part
            return url
        else:
            return json.dumps(data)


def counter(string):
    string = re.sub(r'\s|\w', '', string)
    return len(string)


def verboseOutput(data, name, verbose):
    if core.config.globalVariables['verbose']:
        if str(type(data)) == '<class \'dict\'>':
            try:
                print (json.dumps(data, indent=2))
            except TypeError:
                print (data)
        print (data)


def closest(number, numbers):
    difference = [abs(list(numbers.values())[0]), {}]
    for index, i in numbers.items():
        diff = abs(number - i)
        if diff < difference[0]:
            difference = [diff, {index: i}]
    return difference[1]


def fillHoles(original, new):
    filler = 0
    filled = []
    for x, y in zip(original, new):
        if int(x) == (y + filler):
            filled.append(y)
        else:
            filled.extend([0, y])
            filler += (int(x) - y)
    return filled


def stripper(string, substring, direction='right'):
    done = False
    strippedString = ''
    if direction == 'right':
        string = string[::-1]
    for char in string:
        if char == substring and not done:
            done = True
        else:
            strippedString += char
    if direction == 'right':
        strippedString = strippedString[::-1]
    return strippedString


def extractHeaders(headers):
    headers = headers.replace('\\n', '\n')
    sorted_headers = {}
    matches = re.findall(r'(.*):\s(.*)', headers)
    for match in matches:
        header = match[0]
        value = match[1]
        try:
            if value[-1] == ',':
                value = value[:-1]
            sorted_headers[header] = value
        except IndexError:
            pass
    return sorted_headers


def replaceValue(mapping, old, new, strategy=None):
    """
    Replace old values with new ones following dict strategy.

    The parameter strategy is None per default for inplace operation.
    A copy operation is injected via strateg values like copy.copy
    or copy.deepcopy

    Note: A dict is returned regardless of modifications.
    """
    anotherMap = strategy(mapping) if strategy else mapping
    if old in anotherMap.values():
        for k in anotherMap.keys():
            if anotherMap[k] == old:
                anotherMap[k] = new
    return anotherMap


def getUrl(url, GET):
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
    return ''.join(random.choice((x, y)) for x, y in zip(string.upper(), string.lower()))


def flattenParams(currentParam, params, payload):
    flatted = []
    for name, value in params.items():
        if name == currentParam:
            value = payload
        flatted.append(name + '=' + value)
    return '?' + '&'.join(flatted)


def genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, breaker, special):
    vectors = []
    r = randomUpper  # randomUpper randomly converts chars of a string to uppercase
    for tag in tags:
        if tag == 'd3v' or tag == 'a':
            bait = xsschecker
        else:
            bait = ''
        for eventHandler in eventHandlers:
            # if the tag is compatible with the event handler
            if tag in eventHandlers[eventHandler]:
                for function in functions:
                    for filling in fillings:
                        for eFilling in eFillings:
                            for lFilling in lFillings:
                                for end in ends:
                                    if tag == 'd3v' or tag == 'a':
                                        if '>' in ends:
                                            end = '>'  # we can't use // as > with "a" or "d3v" tag
                                    vector = vector = r(breaker) + special + '<' + r(tag) + filling + r(
                                        eventHandler) + eFilling + '=' + eFilling + function + lFilling + end + bait
                                    vectors.append(vector)
    return vectors


def getParams(url, data, GET):
    params = {}
    if '=' in url:
        data = url.split('?')[1]
        if data[:1] == '?':
            data = data[1:]
    elif data:
        if core.config.globalVariables['jsonData'] or core.config.globalVariables['path']:
            params = data
        else:
            try:
                params = json.loads(data.replace('\'', '"'))
                return params
            except json.decoder.JSONDecodeError:
                pass
    else:
        return None
    if not params:
        parts = data.split('&')
        for part in parts:
            each = part.split('=')
            try:
                params[each[0]] = each[1]
            except IndexError:
                params = None
    return params


def writer(obj, path):
    kind = str(type(obj)).split('\'')[0]
    if kind == 'list' or kind == 'tuple':
        obj = '\n'.join(obj)
    elif kind == 'dict':
        obj = json.dumps(obj, indent=4)
    savefile = open(path, 'w+')
    savefile.write(str(obj.encode('utf-8')))
    savefile.close()


def reader(path):
    with open(path, 'r') as f:
        result = [line.strip(
                    '\n').encode('utf-8').decode('utf-8') for line in f]
    return result
