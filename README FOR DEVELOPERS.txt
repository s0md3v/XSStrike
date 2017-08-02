README FOR DEVELOPERS
I took code from BruteXSS, intellifuzzer, XsScan and WAFNinja. I took the code and made it better. XSStrike isn't just a script which lets you use these programs from one interface. XSStrike's modded modules are far better than the originals and I have added a lot of other things.
BruteXSS and intellifuzzer's code wasn't understanable because intellifuzzer's code was too complicated to understand
while BruteXSS's developer used random variable names for obsfucating the code.
So figured out what is what and added comments to most of the code, so if you find a line with no comment then
either I wasn't able to understand it or it was too obvious and didn't need a comment.
Pick one feature like Striker for example and examine the flow of instructions to understand how it works so you can tweak it.

##################################################
#					WAF Detector
##################################################

Every WAF would block this string <script>alert()</script> because its literally malicious.
So WAF Detector, replaces "d3v" with <script>alert()</script> and makes a request to the injected URL.
Then it checks the http response code,
if the HTTP code is 406 or 501 then its probably mod_security.
if its 999 then the WAF is probably WebKnight.
if its 419 then its F5 BIG IP.
if its 403 then our request got blocked and there exists a WAF but we are not sure which one.
if its 302 then the page is redirecting us.
if HTTP response code is something else other than the codes mentioned above then WAF is not present.

##################################################
				Fuzzer
##################################################

Details The script works by first reading in the URL. If the keyword, XSSHEREXSS is found for one parameter, it continues.
It then tests the URL to see if it can be successfully loaded. If so, the response code is checked to see if the keyword is present.
Without the keyword, a reflected XSS attack is impossible.
If the keyword is found, the script determines the number of times the keyword appears (different attack vectors will be present for each reflection location).
For each reflection, the response is passed to an HTML parser which determines where in the HTML code the reflection is found.
There are several configured locations: an HTML comment, an empty tag attribute, a tag attribute, HTML data or plaintext, or within a script.
Each location has its own function which is called to attempt to generate the correct payload to match the location.
The "break" functions are responsible for determining if an ideal payload will work.
If the ideal payload fails, new tests are run to determine why.
For example, some sites block script tags, but not image tags, so a payload involving image onerror attributes is generated.
If the dynamically generated payloads fail, the function resorts to fuzzing from a lists of paylaods known to work in that specific location.
For example, if the parameter is reflected in an HTML comment, the code --> is appended to the beginning of each payload to ensure the comment is broken out of first.
Every payload attempt is also tested for "cleanliness." This means that, if the ideal payload works, the viewable aspect of the page seen by the victim would not be affected. With some XSS attacks, the escaping needed causes the rest of the page code to become part of the text shown to the visitor. By using a clean attack, the correct code is appended to the end of an attack to allow the page to function generally as it should. For example, if the code was originally: <div attr="param"></div> then the paylaod generated would be: "<script>alert(1);</script><div attr=" The "div attr=" at the end allows a new div to be created in the code, thus preventing HTML syntax errors.
If a clean attack will not work, a warning is given that invalid HTML is being used.
At the conclusion of the script, a full list of possible payloads is provided.
After each occurance, a URL-encoded string is provided as well for easy copy/pasting into the browser.

###########################################
#				Striker
###########################################

1. It takes the URL and parses it so it can seperately use all the parameters present in it.
2. Then it takes the first parameter and injects a payload into it and then makes a request to injected URL.
3. if the payload is found unaltered in the response then the payload works, otherwise not.

###########################################
#				Spider
###########################################

1. It takes the URL and extracts the homepage of the target from it. For example, if the user entered example.com/search.php?q=d3v then it would shorten it to example.com
2. Why homepage? Because homepage has links to nearly all portals available on the target website.
3. So it finds all the links present in the homepage and puts them into a list (except its a pdf or jpg).
4. Then it takes one link from the link list and finds forms in it.
5. If a form is found, it enters a payload into it checks if it got reflected in it.
If doesn't get reflected then it goes back to the previous page and injects the second payload, if that fails as well then the URL is declared non vul.

############################################
#				Ninja
############################################

1. It takes the URL from user and replaces "d3v" with '"(<i=i>)"'. If the response page contains this string then its probably not filtering all the major chars and hence the filter strength is low.
2. If first string is filtered, then it tries <xx src=xx onxx=xx>, if it gets properly reflected in the response then the filter strength is medium.
3, If both strings get filtered then filter strength is declared to be high.
4. After determining the filter strength, it fetchs fuzz strings from the database (db.sqlite) and checks if they are getting filtered.
5. Each fuzzing string has its own nature defined in the database. For example, onload is an event handler.

Here's a list of all string types:
* Event handler: A javascript event handler :p
* url_based : Payloads which use url. For example <object data=example.com/evil.js> or <object data=javascript:alert()>
* error_based : Payloads which use onerror event handler. For example <img src=l onerror=alert()>
* popup_based : Payloads which execute a popup directly by using a suitable event handler like onstart or onload. For example, <svg onload=alert()>
* f_url_based / f_error_based / f_popup_based : These categories are used to store the payload, if the payload from the above three categories gets filtered.
* value : They contain some value. For example, 'test' or (test)
* tag : They are HTML tags like <body> or <br>

6. Once all strings are tested against the target, Ninja prints a table of their status.
7. Now ninja checks if any url_based payload is working, if its working then it prints a url based payload which should work.
If the url_based payload is not working then similarly it checks if the popup_based or error_based payloads are working.

###########################################
#				HULK
###########################################

It replaces "d3v" with a payload and opens it in the browser.
It doesn't check if it works or not. If the payload fails to XSS the target, user can press enter to execute the next payload and open it in browser.