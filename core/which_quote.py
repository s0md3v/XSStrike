from core.make_request import make_request
import re
xsschecker = 'v3dm0s'

def which_quote(OCCURENCE_NUM, url, param_data, method, cookie):
    check_string = 'ST4RTSSX' + xsschecker + '3NDSSX'
    compare_string = 'ST4RTSSX' + xsschecker + '3NDSSX'
    param_data_injected = param_data.replace(xsschecker, check_string)
    try:
        check_response = make_request(url, param_data_injected, method, cookie)
    except:
        check_response = ''
    quote = ''
    occurence_counter = 0
    for m in re.finditer('ST4RTSSX', check_response, re.IGNORECASE):
        occurence_counter += 1
        if occurence_counter == OCCURENCE_NUM and (check_response[(m.start()-1):m.start()] == '\'' or check_response[(m.start()-1):m.start()] == '"'):
            return check_response[(m.start()-1):m.start()]
        elif occurence_counter == OCCURENCE_NUM:
            return quote