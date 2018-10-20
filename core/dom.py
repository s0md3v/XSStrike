import re
from core.colors import red, end, yellow

def dom(response):
    result = False
    highlighted = []
    response = response.split('\n')
    SOURCES_RE = r"""location\.|\.([.\[]\s*["']?\s*arguments|dialogArguments|innerHTML|write|open|showModalDialog|cookie|URL|documentURI|baseURI|referrer|name|opener|parent|top|content|self|frames)\b|(localStorage|sessionStorage|Database)\b"""
    SINKS_RE = r"""( (src|href|data|location|code|value|action)=)|(replace|assign|navigate|getResponseHeader|open|showModalDialog|eval|evaluate|execCommand|execScript|setTimeout|setInterval)\("""
    num = 1
    for newLine in response:
        line = newLine
        pattern = re.findall(SOURCES_RE, line)
        for grp in pattern:
            source = ''.join(grp)
            line = line.replace(source, yellow + source + end)
        pattern = re.findall(SINKS_RE, line)
        for grp in pattern:
            sink = ''.join(grp)
            line = line.replace(sink, red + sink + end)
        if line != newLine:
            highlighted.append('%-3s %s' % (str(num), line.lstrip(' ')))
        num += 1
    if highlighted:
        print (red + ('-' * 60) + end)
        result = True
        for line in highlighted:
            print (line)
        print (red + ('-' * 60) + end)
    return result