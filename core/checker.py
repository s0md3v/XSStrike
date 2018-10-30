import re
import copy
from fuzzywuzzy import fuzz
from core.utils import replacer
from core.config import xsschecker
from urllib.parse import quote_plus
from core.requester import requester

def checker(url, params, headers, GET, delay, payload):
    checkString = 'st4r7' + payload
    paramsCopy = copy.deepcopy(params)
    response = requester(url, replacer(paramsCopy, xsschecker, checkString), headers, GET, delay).text.lower()
    # Itretating over the reflections
    efficiencies = []
    for m in re.finditer('st4r7', response):
        reflected = response[m.start():m.start()+len(checkString)]
        efficiency = fuzz.partial_ratio(reflected, checkString.lower())
        if reflected[-1] == '\\':
            efficiency += 1
        efficiencies.append(efficiency)
    return efficiencies