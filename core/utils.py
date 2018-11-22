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
    string = re.sub(r'\s|\w', '')
    return len(string)


def verboseOutput(data, name, verbose):
    if core.config.globalVariables['verbose']:
        if str(type(data)) == '<class \'dict\'>':
            try:
                print(json.dumps(data, indent=2))
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
    """
    Return URL minus any query part or question mark

    :param url: String of complete URL including possibly a query part
    :param GET: Boolean mode switch for interpreting as GET URL that might contain query part
    :return: guaranteed query part free URL
    """
    return url.split('?', 1)[0] if GET else url


def extractScripts(response):
    scripts = []
    matches = re.findall(r'(?s)<script.*?>(.*?)</script>', response.lower())
    for match in matches:
        if xsschecker in match:
            scripts.append(match)
    return scripts


def randomUpper(string):
    """
    Randomly choose case per character in string

    Optimized local lookup for len(string) invocations

    :param string: string with some case mix
    :return: string with random case mix
    """
    rc = random.choice
    return ''.join(rc(x) for x in zip(string.upper(), string.lower()))


def genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, breaker, special):
    """
    Generate vectors of string from combining and randomizing input parameters.

    :param fillings: Strings that can be used instead of space
    :param eFillings: Characters that can be used between = and JavaScript function or event handler [<svg onload<eFilling>=<eFilling>function()>]
    :param lFillings: Characters that can be used exactly before > in a HTML tag.
    :param eventHandlers: Event handlers and the tags compatible with them to be used while generating payloads
    :param tags: HTML tags to be used while generating payloads.
    :param functions: JavaScript popup functions e.g. alert() or confirm()
    :param ends: Strings to end a HTML tag [> or //]
    :param breaker: String needed to break out of the context
    :param special: The HTML tag which contains the reflection i.e. user input
    :return: vectors of strings from combinations and randomization
    """
    vectors = []
    r = randomUpper  # randomUpper randomly converts chars of a string to uppercase
    for tag in tags:
        bait = 'z' if tag == 'd3v' or tag == 'a' else ''
        for eventHandler in eventHandlers:
            if tag not in eventHandlers[eventHandler]:
                continue
            # if the tag is compatible with the event handler
            for function in functions:
                for filling in fillings:
                    for eFilling in eFillings:
                        for lFilling in lFillings:
                            for end in ends:
                                if (tag == 'd3v' or tag == 'a') and '>' in ends:
                                    end = '>'  # we can't use // as > with "a" or "d3v" tag
                                left = ''.join(
                                    (r(breaker), special, '<', r(tag), filling, r(eventHandler),
                                     eFilling, '=', eFilling, function, lFilling))
                                vectors.append(left + end + bait)
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
    savefile.write(obj)
    savefile.close()


def reader(path):
    with open(path, 'r') as f:
        result = [line.strip(
                    '\n').encode('utf-8').decode('utf-8') for line in f]
    return result
