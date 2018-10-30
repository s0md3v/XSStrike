import re
import copy
from fuzzywuzzy import fuzz
from core.config import xsschecker
from urllib.parse import quote_plus
from core.requester import requester
from core.utils import replacer, fillHoles

def checker(url, params, headers, GET, delay, payload, positions):
    checkString = 'st4r7s' + payload
    paramsCopy = copy.deepcopy(params)
    response = requester(url, replacer(paramsCopy, xsschecker, checkString), headers, GET, delay).text.lower()
    reflectedPositions = []
    for match in re.finditer('st4r7s', response):
        reflectedPositions.append(match.start())
    filledPositions = fillHoles(positions, reflectedPositions)
    # Itretating over the reflections
    efficiencies = []
    for position in reflectedPositions:
        if position:
            reflected = response[position:position+len(checkString)]
            efficiency = fuzz.partial_ratio(reflected, checkString.lower())
            if reflected[-1] == '\\':
                efficiency += 1
            efficiencies.append(efficiency)
        else:
            efficiencies.append(0)
    return efficiencies