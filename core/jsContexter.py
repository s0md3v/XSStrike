import re
from core.config import xsschecker
from core.utils import stripper

def js_contexter(script: str, checker: str = xsschecker) -> str:
    """
    Analyzes a JavaScript script to find a 'breaker' sequence to close open blocks, 
    allowing for payload execution.
    """
    if checker not in script:
        return ""
        
    parts = script.split(checker)
    prefix = parts[0]
    
    # Remove contents between {}, (), "", or '' to focus on the structure
    # This is a heuristic approach from XSStrike original logic
    clean_prefix = re.sub(r'(?s)\{.*?\}|\(.*?\)|".*?"|\'.*?\'', '', prefix)
    
    breaker = []
    for i, char in enumerate(clean_prefix):
        if char == '{':
            breaker.append('}')
        elif char == '(':
            breaker.append(';)') # Original logic: inverted later to );
        elif char == '[':
            breaker.append(']')
        elif char == '/':
            if i + 1 < len(clean_prefix) and clean_prefix[i+1] == '*':
                breaker.append('/*')
        elif char == '}':
            # Remove the last matching closer if we find an existing one in the code
            _pop_if_exists(breaker, '}')
        elif char == ')':
            _pop_if_exists(breaker, ';)')
        elif char == ']':
            _pop_if_exists(breaker, ']')
            
    # Join and reverse the breaker string
    return "".join(breaker)[::-1]

def _pop_if_exists(stack: list, char: str):
    if char in stack:
        stack.remove(char)

# Legacy alias
jsContexter = js_contexter
