import re
from core.config import xsschecker

def jsContexter(script):
    broken = script.split(xsschecker)
    pre = broken[0]
    pre = re.sub(r'(?s)\{.*?\}|(?s)\(.*?\)|(?s)".*?"|(?s)\'.*?\'', '', pre)
    breaker = []
    num = 0
    for char in pre:
        if char == '{':
            breaker.append('}')
        elif char == '(':
            breaker.append(');')
        elif char == '[':
            breaker.append(']')
        elif char == '/':
            try:
                if pre[num + 1] == '*':
                    breaker.append('*/')
            except IndexError:
                pass
        num += 1
    return ''.join(breaker[::-1])