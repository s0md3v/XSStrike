import time
import random
import warnings
import requests
from core.config import timeout, proxy, proxy_cred

warnings.filterwarnings('ignore') # Disable SSL related warnings

def requester(url, data, headers, GET, delay):
    time.sleep(delay)
    user_agents = ['Mozilla/5.0 (X11; Linux i686; rv:60.0) Gecko/20100101 Firefox/60.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991']
    if 'User-Agent' not in headers:
        headers['User-Agent'] = random.choice(user_agents)
    elif headers['User-Agent'] == '$':
        headers['User-Agent'] = random.choice(user_agents)
    proxies = parseProxy()
    print(url)
    if GET:
        response = requests.get(url, params=data, headers=headers, timeout=timeout, proxies=proxies, verify=False)
    else:
        response = requests.post(url, data=data, headers=headers, timeout=timeout, proxies=proxies, verify=False)
    return response

def parseProxy():
    if proxy_cred:
        if proxy.endswith('443') or proxy.endswith('1080'):
            parsedproxy = {'https': 'http://'+proxy_cred+'@'+proxy.split('//')[1]} # HTTPS Proxy
        else:
            parsedproxy = {'http': 'http://'+proxy_cred+'@'+proxy.split('//')[1]} # HTTP Proxy
    else:
        if proxy.endswith('443') or proxy.endswith('1080'):
            parsedproxy = {'https': proxy if 'http' in proxy else 'http://'+proxy} # HTTPS Proxy
        else:
            parsedproxy = {'http': proxy if 'http' in proxy else 'http://'+proxy} # HTTP Proxy
    return parsedproxy
