import re
from core.requester import requester

def wafDetector(url, params, headers, GET, delay, timeout):
    noise = '<script>alert("XSS")</script>' #a payload which is noisy enough to provoke the WAF
    params['xss'] = noise
    response = requester(url, params, headers, GET, delay, timeout) # Opens the noise injected payload
    code = str(response.status_code)
    response_headers = str(response.headers)
    response_text = response.text.lower()
    WAF_Name = ''
    if code[:1] != '2':
        if code == '406' or code == '501': # if the http response code is 406/501
            WAF_Name = 'Mod_Security'
        elif 'wordfence' in response_text:
            WAF_Name = 'Wordfence'
        elif code == '999': # if the http response code is 999
            WAF_Name = 'WebKnight'
        elif 'has disallowed characters' in response_text:
            WAF_Name = 'CodeIgniter'
        elif '<hr><center>nginx</center>' in response_text:
            WAF_Name = 'nginx'
        elif 'comodo' in response_text:
            WAF_Name = 'Comodo'
        elif 'sucuri' in response_text:
            WAF_Name = 'Sucuri'
        elif code == '419': # if the http response code is 419
            WAF_Name = 'F5 BIG IP'
        elif 'barra' in response_headers:
            WAF_Name = 'Barracuda'
        elif re.search(r'cf[-|_]ray', response_headers):
            WAF_Name = 'Cloudflare'
        elif 'AkamaiGHost' in response_headers:
            WAF_Name = 'AkamaiGhost'
        elif code == '403': # if the http response code is 403
            WAF_Name = 'Unknown'
    return WAF_Name