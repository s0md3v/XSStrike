import sys
import requests
from prettytable import PrettyTable # Module for print table of results
from urllib.parse import quote_plus
from core.make_request import make_request
from time import sleep

green = '\033[92m'
red = '\033[91m'
yellow = '\033[93m'
end = '\033[0m'
info = '\033[93m[!]\033[0m'
bad = '\033[91m[-]\033[0m'
run = '\033[97m[~]\033[0m'

# "Not so malicious" payloads for fuzzing
fuzzes = ['<test', '<test//', '<test>', '<test x>', '<test x=y', '<test x=y//',
'<test/oNxX=yYy//', '<test oNxX=yYy>', '<test onload=x', '<test/o%00nload=x',
'<test sRc=xxx', '<test data=asa', '<test data=javascript:asa', '<svg x=y>',
'<details x=y//', '<a href=x//', '<emBed x=y>', '<object x=y//', '<bGsOund sRc=x>',
'<iSinDEx x=y//', '<aUdio x=y>', '<script x=y>', '<script//src=//', '">payload<br/attr="',
'"-confirm``-"', '<test ONdBlcLicK=x>', '<test/oNcoNTeXtMenU=x>', '<test OndRAgOvEr=x>']

def fuzzer(url, param_data, method, delay, xsschecker, cookie):
    result = [] # Result of fuzzing
    progress = 0 # Variable for recording the progress of fuzzing
    for i in fuzzes:
        progress = progress + 1
        sleep(delay) # Pausing the program. Default = 0 sec. In case of WAF = 6 sec. # Pausing the program. Default = 0 sec. In case of WAF = 6 sec.
        sys.stdout.write('\r%s Fuzz Sent: %i/%i' % (run, progress, len(fuzzes)))
        sys.stdout.flush()
        fuzzy = quote_plus(i) # URL encoding the payload
        param_data_injected = param_data.replace(xsschecker, fuzzy) # Replcaing the xsschecker with fuzz
        try:
            if method == 'GET': # GET parameter
                r = requests.get(url + param_data_injected, timeout=10, cookies=cookie) # makes a request to example.search.php?q=<fuzz>
            else: # POST parameter
                r = requests.post(url, data=param_data_injected, timeout=10, cookies=cookie) # Seperating "param_data_injected" with comma because its POST data
            response = r.text
        except:
            print ('\n%s WAF is dropping suspicious requests.' % bad)
            if delay == 0:
                print ('%s Delay has been increased to %s6%s seconds.' % (info, green, end))
                delay += 6
            limit = (delay + 1) * 2
            timer = -1
            while timer < limit:
                sys.stdout.write('\r%s Fuzzing will continue after %s%i%s seconds.' % (info, green, limit, end))
                sys.stdout.flush()
                limit -= 1
                sleep(1)
            try:
                requests.get(url, timeout=5, cookies=cookie)
                print ('\n%s Pheww! Looks like sleeping for %s%i%s seconds worked!' % (good, green, (delay + 1) * 2), end)
            except:
                print ('\n%s Looks like WAF has blocked our IP Address. Sorry!' % bad)
                break
        if i in response: # if fuzz string is reflected in the response / source code
            result.append({
            'result' : '%sWorks%s' % (green, end),
            'fuzz' : i})
        elif str(r.status_code)[:1] != '2': # if the server returned an error (Maybe WAF blocked it)
            result.append({
            'result' : '%sBlocked%s'  % (red, end),
            'fuzz' : i})
        else: # if the fuzz string was not reflected in the response completely
            result.append({
                'result' : '%sFiltered%s' % (yellow, end),
                'fuzz' : i})
    table = PrettyTable(['Fuzz', 'Response']) # Creates a table with two columns
    for value in result:
        table.add_row([value['fuzz'], value['result']]) # Adds the value of fuzz and result to the columns
    print('\n', table)
    quit()