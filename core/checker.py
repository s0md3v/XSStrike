import copy
import re
from urllib.parse import unquote
from fuzzywuzzy import fuzz
from typing import List

from core.requester import requester
from core.utils import replaceValue, fillHoles
from core.config import ScanContext

class XSSChecker:
    def __init__(self, context: ScanContext):
        self.context = context

    def check(self, payload: str, positions: List[int]) -> List[int]:
        """
        Checks the efficiency of a payload by analyzing reflections in the response.
        """
        check_string = 'st4r7s' + payload + '3nd'
        encoding = self.context.encoding
        
        if encoding:
            check_string = encoding(unquote(check_string))
            
        # Replace the placeholder in params with our probe
        probe_params = replaceValue(
            self.context.paramData, 
            self.context.config.xsschecker, 
            check_string, 
            copy.deepcopy
        )
        
        response_text = requester(
            self.context.target, 
            probe_params, 
            self.context.headers, 
            True, # GET (Legacy)
            self.context.config.delay, 
            self.context.config.timeout
        ).text.lower()
        
        reflected_positions = [match.start() for match in re.finditer('st4r7s', response_text)]
        filled_positions = fillHoles(positions, reflected_positions)
        
        efficiencies = []
        for i, position in enumerate(filled_positions):
            all_efficiencies = []
            try:
                reflected = response_text[reflected_positions[i]:reflected_positions[i] + len(check_string)]
                efficiency = fuzz.partial_ratio(reflected, check_string.lower())
                all_efficiencies.append(efficiency)
            except IndexError:
                pass
                
            if position:
                reflected = response_text[position:position + len(check_string)]
                if encoding:
                    check_string = encoding(check_string.lower())
                efficiency = fuzz.partial_ratio(reflected, check_string)
                
                # Special case for escaped backslash
                if reflected[:-2] == ('\\%s' % check_string.replace('st4r7s', '').replace('3nd', '')):
                    efficiency = 90
                all_efficiencies.append(efficiency)
                efficiencies.append(max(all_efficiencies))
            else:
                efficiencies.append(0)
                
        return [eff for eff in efficiencies if eff > 0]
