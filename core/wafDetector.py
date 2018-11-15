import json
import re

from core.requester import requester

def wafDetector(url, params, headers, GET, delay, timeout):
    with open('./db/wafSignatures.json', 'r') as file:
        wafSignatures = json.load(file)
    noise = '<script>alert("XSS")</script>' #a payload which is noisy enough to provoke the WAF
    params['xss'] = noise
    response = requester(url, params, headers, GET, delay, timeout) # Opens the noise injected payload
    page = response.text
    code = str(response.status_code)
    headers = str(response.headers)
    if int(code) >= 400:
        bestMatch = [0, None]
        for wafName, wafSignature in wafSignatures.items():
            score = 0
            pageSign = wafSignature['page']
            codeSign = wafSignature['code']
            headersSign = wafSignature['headers']
            if pageSign:
                if re.search(pageSign, page, re.I):
                    score += 1
            if codeSign:
                if re.search(codeSign, code, re.I):
                    score += 0.5
            if headersSign:
                if re.search(headersSign, headers, re.I):
                    score += 1
            if score > bestMatch[0]:
                del bestMatch[:]
                bestMatch.extend([score, wafName])
        if bestMatch[0] != 0:
            return bestMatch[1]
        else:
            return None
    else:
        return None
