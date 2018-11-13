import copy
import requests
from time import sleep
from random import randint
from core.utils import replacer
from core.requester import requester
from core.config import fuzzes, xsschecker
from urllib.parse import quote_plus, unquote
from core.colors import end, red, white, green, yellow, run, bad, good, info, que

def counter(string):
    special = '\'"=/:*&)(}{][><'
    count = 0
    for char in list(string):
        if char in special:
            count += 1
    return count

def fuzzer(url, params, headers, GET, delay, timeout, WAF, encoding):
    for fuzz in fuzzes:
        if delay == 0:
            delay = 0
        t = delay + randint(delay, delay * 2) + counter(fuzz)
        sleep(t)
        paramsCopy = copy.deepcopy(params)
        try:
            if encoding:
                fuzz = encoding(unquote(fuzz))
            data = replacer(paramsCopy, xsschecker, fuzz)
            response = requester(url, data, headers, GET, delay/2, timeout)
        except:
            print ('\n%s WAF is dropping suspicious requests.' % bad)
            if delay == 0:
                print ('%s Delay has been increased to %s6%s seconds.' % (info, green, end))
                delay += 6
            limit = (delay + 1) * 50
            timer = -1
            while timer < limit:
                print ('\r%s Fuzzing will continue after %s%i%s seconds.\t\t' % (info, green, limit, end), end='\r')
                limit -= 1
                sleep(1)
            try:
                requests.get(url, timeout=5, headers=headers)
                print ('\n%s Pheww! Looks like sleeping for %s%i%s seconds worked!' % (good, green, (delay + 1) * 2), end)
            except:
                print ('\n%s Looks like WAF has blocked our IP Address. Sorry!' % bad)
                break
        if encoding:
            fuzz = encoding(fuzz)
        if fuzz.lower() in response.text.lower(): # if fuzz string is reflected in the response
            result = ('%s[passed]  %s' % (green, end))
        elif str(response.status_code)[:1] != '2': # if the server returned an error (Maybe WAF blocked it)
            result = ('%s[blocked] %s' % (red, end))
        else: # if the fuzz string was not reflected in the response completely
            result = ('%s[filtered]%s' % (yellow, end))
        print ('%s %s' % (result, fuzz))
