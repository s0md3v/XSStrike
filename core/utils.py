import re
import json
import random
from core.config import xsschecker
from core.colors import info, red, end

def verboseOutput(data, name, verbose):
    if verbose:
        print ('%s %s %s%s%s' % (info, name, red, ('-' * 50), end))
        if str(type(data)) == '<class \'dict\'>':
            try:
                print (json.dumps(data, indent=2))
            except TypeError:
                print (data)
        print (data)
        print ('%s%s%s' % (red, ('-' * 60), end))

def closest(number, numbers):
    difference = [abs(list(numbers.values())[0]), {}]
    for index, i in numbers.items():
        diff = abs(number - i)
        if diff < difference[0]:
            difference = [diff, {index : i}]
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

def replacer(dic, toReplace, replaceWith):
    for key in dic.keys():
        if dic[key] == toReplace:
            dic[key] = replaceWith
    return dic

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