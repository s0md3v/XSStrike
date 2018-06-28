import requests
import re
from urllib.parse import quote_plus

bad = '\033[91m[-]\033[0m'
good = '\033[32m[+]\033[0m'

def WAF_detector(url, param_data, method, xsschecker, cookie):
    global WAF
    WAF = False
    noise = quote_plus('<script>alert()</script>') #a payload which is noisy enough to provoke the WAF
    fuzz = param_data.replace(xsschecker, noise) #Replaces xsschecker in param_data with noise
    if method == 'GET':
        response = requests.get(url + fuzz, cookies=cookie) # Opens the noise injected payload
    else:
        response = requests.post(url, data=fuzz, cookies=cookie) # Opens the noise injected payload
    code = str(response.status_code)
    response_headers = str(response.headers)
    response_text = response.text.lower()
    if code[:1] != '2':
        if '406' == code or '501' == code: # if the http response code is 406/501
            WAF_Name = 'Mod_Security'
            WAF = True
        elif 'wordfence' in response_text:
            WAF_Name = 'Wordfence'
            WAF = True
        elif '999' == code: # if the http response code is 999
            WAF_Name = 'WebKnight'
            WAF = True
        elif 'has disallowed characters' in response_text:
            WAF_Name = 'CodeIgniter'
            WAF = True
        elif '<hr><center>nginx</center>' in response_text:
            WAF_Name = 'nginx'
            WAF = True
        elif 'comodo' in response_text:
            WAF_Name = 'Comodo'
            WAF = True
        elif 'sucuri' in response_text:
            WAF_Name = 'Sucuri'
            WAF = True
        elif '419' == code: # if the http response code is 419
            WAF_Name = 'F5 BIG IP'
            WAF = True
        elif 'barra' in response_headers:
            WAF_Name = 'Barracuda'
            WAF = True
        elif re.search(r'cf[-|_]ray', response_headers):
            WAF_Name = 'Cloudflare'
            WAF = True
        elif 'AkamaiGHost' in response_headers:
            WAF_Name = 'AkamaiGhost'
            WAF = True
        elif '403' == code: # if the http response code is 403
            WAF_Name = 'Unknown'
            WAF = True
    else:
        print('%s WAF Status: Offline' % good)
        return False
    if WAF:
        print('%s WAF Detected: %s' % (bad, WAF_Name))
        return True
