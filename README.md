<p align="middle"><img src='https://i.imgur.com/TKMnPRJ.png' /></p>

<a href="http://xsstrike.tk">![Website](https://img.shields.io/website-up-down-green-red/http/shields.io.svg?label=xsstrike.tk&style=flat-square)</a> ![Python](https://img.shields.io/badge/Requires-Python2.7-blue.svg) ![Version](https://img.shields.io/badge/Version-1.2-red.svg) ![Bugs](https://img.shields.io/badge/Known--Issues-0-yellow.svg)                     

# XSStrike
XSStrike is a python script designed to detect and exploit XSS vulnerabilites. Visit XSStrike's [project site](http://xsstrike.tk/) for more info.

A list of features XSStrike has to offer:

- [x] Fuzzes a parameter and builds a suitable payload
- [x] Bruteforces paramteres with payloads
- [x] Has an inbuilt crawler like functionality
- [x] Can reverse engineer the rules of a WAF/Filter
- [x] Detects and tries to bypass WAFs
- [x] Both GET and POST support
- [x] Most of the payloads are hand crafted
- [x] Negligible number of false positives
- [x] Opens the POC in a browser window

<img src='https://i.imgur.com/oWVlUjs.png' />

### Installing XSStrike
Use the following command to download it
```
git clone https://github.com/UltimateHackers/XSStrike/
```
After downloading, navigate to XSStrike directory with the following command
```
cd XSStrike
```
Now install the required modules with the following command
```
pip install -r requirements.txt
```
Now you are good to go! Run XSStrike with the following command
```
python xsstrike
```
### Using XSStrike
You can enter <b>help</b> in XSStrike's target prompt for basic usages.

You can view XSStrike's complete documentation [here](http://xsstrike.tk/Documentation/).

## Are you a Developer?
If you are a developer and want to use XSStrike's code in your project or want to contribute to XSStrike then you should read the [developer guide](http://xsstrike.tk/For-Developers/).

#### Credits
XSStrike uses code from [BruteXSS](https://github.com/shawarkhanethicalhacker/BruteXSS), [Intellifuzzer-XSS](https://github.com/matthewdfuller/intellifuzz-xss) and [XsScan](https://github.com/The404Hacking/XsSCan), [WAFNinja](https://github.com/khalilbijjou/WAFNinja/).
