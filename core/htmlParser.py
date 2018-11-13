import re
from core.config import badTags
from core.encoders import base64
from core.config import xsschecker

def htmlParser(response, encoding):
    rawResponse = response
    response = response.text
    if encoding:
        response = response.replace(encoding(xsschecker), xsschecker)
    tags = [] # tags in which the input is reflected
    locations = [] # contexts in which the input is reflected
    attributes = [] # attribute names
    environments = [] # strings needed to break out of the context
    positions = []
    for match in re.finditer(xsschecker, response):
        positions.append(match.start())
    parts = response.split(xsschecker)
    parts.remove(parts[0]) # remove first element since it doesn't contain xsschecker
    parts = [xsschecker + s for s in parts] # add xsschecker in front of all elements
    for part in parts: # iterate over the parts
        deep = part.split('>')
        if '</script' in deep[0]:
            location = 'script'
        elif '</' in deep[0]:
            location = 'html'
        else:
            for i in deep:
                if i[-2:] == '--':
                    if '<!--' not in i:
                        location = 'comment'
                        break
                        continue
                location = 'script'
                for char in part:
                    if char == '<':
                        location = 'attribute'
                        break
        if '<' not in response:
            if rawResponse.headers['Content-Type'] == 'text/html':
                location = 'html'
        locations.append(location) # add location to locations list
    num = 0 # dummy value to keep record of occurence being processed
    for occ in re.finditer(xsschecker, response, re.IGNORECASE): # find xsschecker in response and return matches
        toLook = list(response[occ.end():]) # convert "xsschecker to EOF" into a list
        for loc in range(len(toLook)): # interate over the chars
            if toLook[loc] in ('\'', '"', '`'): # if the char is a quote
                environments.append(toLook[loc]) # add it to enviornemts list
                tokens = response.split('<')
                goodTokens = [] # tokens which contain xsschecker
                for token in tokens: # iterate over tokens
                    if xsschecker in token: # if xsschecker is in token
                        goodTokens.append(token) # add it to goodTokens list
                        attrs = token.split(' ')
                        for attr in attrs:
                            if xsschecker in attr:
                                attributes.append(attr.split('=')[0])
                                break
                try:
                    tag = re.search(r'\w+', goodTokens[num]).group() # finds the tag "inside" which input is refelcted
                except IndexError:
                    try:
                        tag = re.search(r'\w+', goodTokens[num - 1]).group() # finds the tag "inside" which input is refelcted
                    except IndexError:
                        tag = 'null'
                tags.append(tag) # add the tag to the tags
                break
            elif toLook[loc] == '<':
                if toLook[loc + 1] == '/':
                    tag = ''.join(toLook).split('</')[1].split('>')[0]
                    if tag in badTags:
                        environments.append('</' + tag + '/>')
                    else:
                        environments.append('')
                    tags.append(tag)
                    attributes.append('')
                break
            loc += 1
        num += 1
    occurences = {}
    for i, loc, env, tag, attr, position in zip(range(len(locations)), locations, environments, tags, attributes, positions):
        occurences[i] = {}
        if loc == 'comment':
            value = '-->'
        occurences[i]['position'] = position
        occurences[i]['context'] = [loc, env, tag, attr]
    return [occurences, positions]
