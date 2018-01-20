# XSStrike [![python](https://img.shields.io/badge/Python-2.7-green.svg?style=style=flat-square)](https://www.python.org/downloads/) [![version](https://img.shields.io/badge/Version-Pre_Beta-blue.svg?style=style=flat-square)](https://twitter.com/s0md3v) [![license](https://img.shields.io/badge/License-GPL_3-orange.svg?style=style=flat-square)](https://github.com/UltimateHacke/XSStrike/blob/master/license.txt)

![banner](https://i.imgur.com/3t2X0dX.png)

XSStrike is an advanced XSS detection suite. It has a powerful fuzzing engine and provides zero false positive result using fuzzy matching. XSStrike is the first XSS scanner to generate its own payloads. It is intelligent enough to detect and break out of various contexts.

Made with ![heart](https://cloud.githubusercontent.com/assets/4301109/16754758/82e3a63c-4813-11e6-9430-6015d98aeaab.png) by <a href=https://twitter.com/s0md3v>Somdev Sangwan</a>

## Features
- GET & POST method support
- Cookie Support
- WAF Fingerprinting
- Hand crafted payloads for filter and WAF evasion
- Powerful fuzzing engine
- Context breaking technology
- Intelligent payload generation
- Accurate results via <a href=https://en.wikipedia.org/wiki/Levenshtein_distance>levenshtein distance</a> algorithm
more to come...

### Installation
XSStrike is compatible with all \*nix based operating systems running Python 2.7.
Why not windows? My life, my rules. My code, my tools. Just kidding, it will run on windows as well but you will see some weird codes instead of color.
First of all clone the repo by entering the following command in terminal
``` bash
git clone https://github.com/UltimateHackers/XSStrike
```
Now naviagte to XSStrike directory
``` bash
cd XSStrike
```
Now install the requirements with the following command
``` bash
pip install -r requirements.txt
```
Now you can run XSStrike
``` bash
python xsstrike
```
### Screenshots
![ss1](https://i.imgur.com/CdPWwlw.png)
![ss2](https://i.imgur.com/BEAVRAA.png)

#### Contribution & Sponsorship
Want to contribute? What are you waiting for? Fork it and hit up with a pull request.
Want to sponsor? Mail me at s0md3v@gmail.com
