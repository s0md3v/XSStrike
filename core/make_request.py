import requests
import random
from time import sleep
from urllib.parse import urlparse as parsy, parse_qs

bad = '\033[91m[-]\033[0m'

user_agents = ['Mozilla/5.0 (X11; Linux i686; rv:60.0) Gecko/20100101 Firefox/60.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991']

def make_request(url, param_data, method, cookie): #The main function which actually makes contact with the target
    headers = {
    'Host' : parsy(url).hostname,
    'User-Agent' : random.choice(user_agents),
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language' : 'en-US,en;q=0.5',
    'Accept-Encoding' : 'deflate',
    'DNT' : '1',
    'Connection' : 'close'}
    try:
        if method == 'GET':
            resp = requests.get(url + param_data, cookies=cookie, headers=headers) #Makes request
            return resp.text #Reads the output
        elif method == 'POST':
            resp = requests.post(url, data=dict(parse_qs(param_data)), cookies=cookie, headers=headers) #Makes request
            return resp.text #Reads the output
    except:
        print('\n%s Target isn\'t responding properly.' % bad)
        quit()
