import base64 as b64
import re


def base64(string):
    if re.match(r'^[A-Za-z0-9+\/=]+$', string) and (len(string) % 4) == 0:
        return b64.b64decode(string.encode('utf-8')).decode('utf-8')
    else:
        return b64.b64encode(string.encode('utf-8')).decode('utf-8')
