import re
import webbrowser
from core.make_request import make_request
from fuzzywuzzy import fuzz # Module for fuzzy matching

que = '\033[94m[?]\033[0m'
good = '\033[32m[+]\033[0m'

xsschecker = 'v3dm0s'

def test_param_check(payload_to_check, payload_to_compare, OCCURENCE_NUM, url, param_data, method, action, cookie):
    check_string = 'st4r7' + payload_to_check + '3nds' # We are adding st4r7 and 3nds to make
    compare_string = 'st4r7' + payload_to_compare + '3nds' # the payload distinguishable in the response
    param_data_injected = param_data.replace(xsschecker, check_string)
    check_response = make_request(url, param_data_injected, method, cookie)
    success = False
    occurence_counter = 0 # Variable to keep track of which reflection is going through the loop
    # Itretating over the reflections
    for m in re.finditer('st4r7', check_response, re.IGNORECASE):
        occurence_counter = occurence_counter + 1
        efficiency = fuzz.partial_ratio(check_response[m.start():m.start()+len(compare_string)].lower(), compare_string.lower())
        if efficiency == 100:
            if action == 'do':
                print('\n%s Payload: %s' % (good, payload_to_compare))
                print('%s Efficiency: 100%%' % good)
                choice = input('%s A payload with 100%% efficiency was found. Continue scanning? [y/N] ' % que).lower()
                if choice == 'y':
                    pass
                else:
                    if method == 'GET':
                        webbrowser.open(url+param_data.replace(xsschecker, payload_to_compare))
                        quit()
            if occurence_counter == OCCURENCE_NUM:
                success = True
            break
        
        if efficiency > 90 and action == 'do':
            print('\n%s Payload: %s' % (good, payload_to_compare))
            print('%s Efficiency: %s' % (good, efficiency))
            try:
                data_type = occur_location[OCCURENCE_NUM - 1]
                if data_type == 'comment':
                    location_readable = 'inside a HTML comment '
                elif data_type == 'html':
                    location_readable = 'as data or plaintext on the page'
                elif data_type == 'script':
                    location_readable = 'as data in javascript'
                elif data_type == 'attribute':
                    location_readable = 'as an attribute in a HTML tag'
                print('%s Location: %s' % (good, location_readable))
                break
            except:
                continue
    return success