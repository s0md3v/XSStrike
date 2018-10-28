import re
from core.utils import stripper
from core.config import xsschecker

def jsContexter(script):
    broken = script.split(xsschecker)
    pre = broken[0]
    pre = re.sub(r'(?s)\{.*?\}|(?s)\(.*?\)|(?s)".*?"|(?s)\'.*?\'', '', pre)
    breaker = ''
    num = 0
    for char in pre:
        if char == '{':
            breaker += '}'
        elif char == '(':
            breaker += ';)'
        elif char == '[':
            breaker += ']'
        elif char == '/':
            try:
                if pre[num + 1] == '*':
                    breaker += '/*'
            except IndexError:
                pass
        elif char == '}':
            breaker = stripper(breaker, '}')
        elif char == ')':
            breaker = stripper(breaker, ')')
        elif breaker == ']':
            breaker = stripper(breaker, ']')
        num += 1
    return breaker[::-1]