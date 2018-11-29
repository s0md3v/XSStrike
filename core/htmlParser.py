import re

from core.config import badTags, xsschecker


def htmlParser(response, encoding):
    rawResponse = response  # raw response returned by requests
    response = response.text  # response content
    if encoding:  # if the user has specified an encoding, encode the probe in that
        response = response.replace(encoding(xsschecker), xsschecker)
    tags = []  # tags in which the input is reflected
    locations = []  # contexts in which the input is reflected
    attributes = []  # attribute names
    environments = []  # strings needed to break out of the context
    positions = []  # postions of all the reflections of the xsschecker
    for match in re.finditer(xsschecker, response):
        positions.append(match.start())

#  It finds the contexts of the reflections

    parts = response.split(xsschecker)
    # remove first element since it doesn't contain xsschecker
    parts.remove(parts[0])
    # add xsschecker in front of all elements
    parts = [xsschecker + s for s in parts]
    for part in parts:  # iterate over the parts
        deep = part.split('>')
        if '</script' in deep[0]:
            location = 'script'
        elif '</' in deep[0]:
            location = 'html'
        else:
            num = 0
            for i in deep:
                if i[-2:] == '--':
                    if '<!--' not in ''.join(deep[:num + 1]):
                        location = 'comment'
                        break
                        continue
                location = 'script'
                for char in part:
                    # the only way to find out if it's attribute context is to see if '<' is present.
                    if char == '<':
                        location = 'attribute'  # no, it doesn't match '<script>'
                        break
                num += 1
        if '<' not in response:
            if rawResponse.headers['Content-Type'].startswith('text/html'):
                location = 'html'
        locations.append(location)  # add location to locations list

#  Finds the "environment" of reflections. is it within double quotes? Which tag contains the reflection?

    num = 0  # dummy value to keep record of occurence being processed
    # find xsschecker in response and return matches
    for occ in re.finditer(xsschecker, response, re.IGNORECASE):
        # convert "xsschecker to EOF" into a list
        toLook = list(response[occ.end():])
        for loc in range(len(toLook)):  # interate over the chars
            if toLook[loc] in ('\'', '"', '`'):  # if the char is a quote
                environments.append(toLook[loc])  # add it to enviornemts list
                tokens = response.split('<')
                goodTokens = []  # tokens which contain xsschecker
                for token in tokens:  # iterate over tokens
                    if xsschecker in token:  # if xsschecker is in token
                        goodTokens.append(token)  # add it to goodTokens list
                        # attributes and their values are generally seperated with space so...
                        attrs = token.split(' ')
                        for attr in attrs:  # iterate over the attribute
                            if xsschecker in attr:  # is xsschecker in this attribute?
                                # alright, this is the one we need
                                attributeName = attr.split('=')[0]
                                attributeValue = ''.join(attr.split('=')[1:])
                                if attributeValue.startswith('\'') or attributeValue.startswith('"'):
                                    attributeValue = attributeValue[1:-1]
                                attributes.append({attributeName:attributeValue})
                                break
                try:
                    # finds the tag "inside" which input is refelcted
                    tag = re.search(r'\w+', goodTokens[num]).group()
                except IndexError:
                    try:
                        # finds the tag "inside" which input is refelcted
                        tag = re.search(r'\w+', goodTokens[num - 1]).group()
                    except IndexError:
                        tag = 'null'
                tags.append(tag)  # add the tag to the tags list
                break
            elif toLook[loc] == '<':  # if we encounter a closing angular brackt
                # check if the next character to it is a / to make sure its a closing tag
                if toLook[loc + 1] == '/':
                    tag = ''.join(toLook).split('</')[1].split('>')[0]
                    if tag in badTags:  # if the tag is a non-executable context e.g. noscript, textarea
                        # add it to environments because we need to break out of it
                        environments.append('</' + tag + '/>')
                    else:
                        environments.append('')
                    tags.append(tag)  # add the tag to tags list
                    # since it's a closing tag, it can't have any attributes
                    attributes.append('')
                break
            loc += 1
        num += 1
    occurences = {}  # a dict to store all the collected information about the reflections
    for i, loc, env, tag, attr, position in zip(range(len(locations)), locations, environments, tags, attributes, positions):
        occurences[i] = {}
        occurences[i]['position'] = position
        if loc == 'comment':  # if context is html comment
            env = '-->'  # add --> as environment as we need this to break out
        occurences[i]['context'] = [loc, env, tag, attr]
    return [occurences, positions]
