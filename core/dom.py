import re
from core.colors import red, end, yellow

def dom(response):
    highlighted = []
    response = response.split('\n')
    sources = r"""location\.|\.([.\[]\s*["']?\s*arguments|dialogArguments|innerHTML|write|open|showModalDialog|cookie|URL|documentURI|baseURI|referrer|name|opener|parent|top|content|self|frames)[^\w\-]|(localStorage|sessionStorage|Database)[^\w\-]"""
    sinks = r"""( (src|href|data|location|code|value|action)=)|(replace|assign|navigate|getResponseHeader|open|showModalDialog|eval|evaluate|execCommand|execScript|setTimeout|setInterval)\("""
    num = 1
    try:
        for newLine in response:
            line = newLine
            pattern = re.findall(sources, line)
            for grp in pattern:
                source = ''.join(grp)
                line = line.replace(source, yellow + source + end)
            pattern = re.findall(sinks, line)
            for grp in pattern:
                sink = ''.join(grp)
                line = line.replace(sink, red + sink + end)
            if line != newLine:
                highlighted.append('%-3s %s' % (str(num), line.lstrip(' ')))
            num += 1
    except MemoryError:
        pass
    return highlighted
