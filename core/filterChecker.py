from core.checker import checker


def filterChecker(url, params, headers, GET, delay, occurences, timeout, encoding):
    positions = {}
    sortedEfficiencies = {}
    # adding < > to environments anyway because they can be used in all contexts
    environments = set(['<', '>'])
    for i in range(len(occurences)):
        sortedEfficiencies[i] = {}
    for i, occurence in zip(range(len(occurences)), occurences.values()):
        environments.add(occurence['context'][1])
        location = occurence['context'][0]
        try:
            attributeName = list(occurence['context'][3].keys())[0]
            attributeValue = list(occurence['context'][3].values())[0]
        except AttributeError:
            attributeName = occurence['context'][3]
        positions[str(i)] = occurence['position']
        if location == 'comment':
            environments.add('-->')
        elif location == 'script':
            environments.add('</scRipT/>')
        elif attributeName == 'srcdoc':  # srcdoc attribute accepts html data with html entity encoding
            environments.add('&lt;')  # so let's add the html entity
            environments.add('&gt;')  # encoded versions of < and >

    for environment in environments:
        if environment == '':
            efficiencies = [100 for i in range(len(occurences))]
        else:
            efficiencies = checker(
                url, params, headers, GET, delay, environment, positions, timeout, encoding)
            if len(efficiencies) < len(occurences):
                for i in range(len(occurences) - len(efficiencies)):
                    efficiencies.append(0)
        for i, efficiency in zip(range(len(efficiencies)), efficiencies):
            try:
                sortedEfficiencies[i][environment] = efficiency
            except:
                sortedEfficiencies[i] = {}
                sortedEfficiencies[i][environment] = efficiency
    for efficiency, occurence in zip(sortedEfficiencies.values(), occurences.values()):
        occurence['score'] = efficiency
    return occurences
