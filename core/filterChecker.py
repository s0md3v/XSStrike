from core.utils import replacer
from core.checker import checker
from core.config import xsschecker
from core.requester import requester

def filterChecker(url, params, headers, GET, delay, occurences, timeout, encoding):
    positions = {}
    environments = set(['<', '>'])
    sortedEfficiencies = {}
    for i in range(len(occurences)):
        sortedEfficiencies[i] = {}
    for i, occurence in zip(range(len(occurences)), occurences.values()):
        environments.add(occurence['context'][1])
        location = occurence['context'][0]
        attribute = occurence['context'][3]
        positions[str(i)] = occurence['position']
        if location == 'comment':
            environments.add('-->')
        elif location == 'script':
            environments.add('</scRipT/>')
        elif attribute == 'srcdoc':
            environments.add('&lt;')
            environments.add('&gt;')
    for environment in environments:
        if environment == '':
            efficiencies = [100 for i in range(len(occurences))]
        else:
            efficiencies = checker(url, params, headers, GET, delay, environment, positions, timeout, encoding)
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