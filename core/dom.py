import re

from core.colors import red, end, yellow


def dom(response):
    highlighted = []
    allControlledVariables = set()
    response = response.split('\n')
    sources = r"""location\.|\.([.\[]\s*["']?\s*arguments|dialogArguments|innerHTML|write|open|showModalDialog|cookie|URL|documentURI|baseURI|referrer|name|opener|parent|top|content|self|frames)[^\w\-]|(localStorage|sessionStorage|Database)[^\w\-]"""
    sinks = r"""( (src|href|data|location|code|value|action)=)|(replace|assign|navigate|getResponseHeader|open|showModalDialog|eval|evaluate|execCommand|execScript|setTimeout|setInterval)\("""
    num = 1
    try:
        for newLine in response:
            line = newLine
            parts = line.split('var ')
            controlledVariables = set()
            if len(parts) > 1:
                for part in parts:
                    for controlledVariable in allControlledVariables:
                        if controlledVariable in part:
                            controlledVariables.add(part.split(' ')[0])
            pattern = re.findall(sources, newLine)
            for grp in pattern:
                source = ''.join(grp)
                if source:
                    parts = newLine.split('var ')
                    for part in parts:
                        if source in part:
                            controlledVariables.add(part.split(' ')[0])
                    line = line.replace(source, yellow + source + end)
            for controlledVariable in controlledVariables:
                allControlledVariables.add(controlledVariable)
            for controlledVariable in allControlledVariables:
                matches = list(filter(None, re.findall(r'\b%s\b' % controlledVariable, line)))
                if matches:
                    line = re.sub(r'\b%s\b' % controlledVariable, yellow + controlledVariable + end, line)
            pattern = re.findall(sinks, newLine)
            for grp in pattern:
                sink = ''.join(grp)
                if sink:
                    line = line.replace(sink, red + sink + end)
            if line != newLine:
                highlighted.append('%-3s %s' % (str(num), line.lstrip(' ')))
            num += 1
    except MemoryError:
        pass
    return highlighted
