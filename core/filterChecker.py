from core.utils import replacer
from core.checker import checker
from core.config import xsschecker
from core.requester import requester

def filterChecker(url, params, headers, GET, delay, occurences):
    environments = set(['<', '>'])
    sortedEfficiencies = {}
    for i in range(len(occurences) + 10):
        sortedEfficiencies[i] = {}
    for occurence in occurences.values():
        environments.add(occurence['context'][1])
        location = occurence['context'][0]
        if location == 'comment':
            environments.add('-->')
        elif location == 'script':
            environments.add('</scRipT/>')
    for environment in environments:
        if environment == '':
            efficiencies = [100 for i in range(len(occurences))]
        else:
            efficiencies = checker(url, params, headers, GET, delay, environment)
            if not efficiencies:
                for i in range(len(occurences)):
                    efficiencies.append(0)
        for i, efficiency in zip(range(len(efficiencies)), efficiencies):
            sortedEfficiencies[i][environment] = efficiency
    for efficiency, occurence in zip(sortedEfficiencies.values(), occurences.values()):
        occurence['score'] = efficiency
    return occurences