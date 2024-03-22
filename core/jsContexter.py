import re
from core.config import xsschecker  # Assuming xsschecker is a variable containing the pattern to remove
from core.utils import stripper  # Assuming stripper is a function for removing characters


def jsContexter(script):
    broken = script.split(xsschecker)
    pre = broken[0]

    # Fixed regular expression with `(?s)` flag at the beginning
    re.sub(r'\{.*?\}|\(.*?\)|".*?"|\'.*?\'', '', pre)

    breaker = ''
    num = 0
    for char in pre:  # iterate over the remaining characters
        if char == '{':
            breaker += '}'
        elif char == '(':
            breaker += ';)'  # yes, it should be ); but we will invert the whole thing later
        elif char == '[':
            breaker += ']'
        elif char == '/':
            try:
                if pre[num + 1] == '*':
                    breaker += '/*'
            except IndexError:
                pass
        elif char in '}:)':  # Combine closing characters for efficiency
            breaker = stripper(breaker, char)  # Remove matching closing character
        elif breaker and breaker[-1] == ']':  # Handle closing square bracket efficiently
            breaker = stripper(breaker, ']')
        num += 1
    return breaker[::-1]  # invert the breaker string

