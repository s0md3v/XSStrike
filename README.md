# XSStrike [![python](https://img.shields.io/badge/Python-2.7-green.svg?style=style=flat-square)](https://www.python.org/downloads/) [![version](https://img.shields.io/badge/Version-Beta-blue.svg?style=style=flat-square)](https://twitter.com/s0md3v) [![license](https://img.shields.io/badge/License-GPL_3-orange.svg?style=style=flat-square)](https://github.com/UltimateHacke/XSStrike/blob/master/license.txt)

![banner](https://image.ibb.co/dSSbF8/68747470733a2f2f692e696d6775722e636f6d2f4a3237756f52492e706e67.png)

XSStrike is an advanced XSS detection suite. It has a powerful fuzzing engine and provides zero false positive result using fuzzy matching. XSStrike is the first XSS scanner to generate its own payloads. It is intelligent enough to detect and break out of various contexts.

Made with ![heart](https://cloud.githubusercontent.com/assets/4301109/16754758/82e3a63c-4813-11e6-9430-6015d98aeaab.png) by [Somdev Sangwan](https://twitter.com/s0md3v)

## Features
- Powerful fuzzing engine
- Context breaking technology
- Intelligent payload generation
- GET & POST method support
- Cookie Support
- WAF Fingerprinting
- Hand crafted payloads for filter and WAF evasion
- Hidden parameter discovery
- Accurate results via [levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) algorithm

To know more visit [xsstrike.tk](http://xsstrike.tk)

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

![ss1](https://image.ibb.co/hFAVa8/68747470733a2f2f7873737472696b652e746b2f696d616765732f312e706e67.png)

![ss2](https://image.ibb.co/jA9dTT/68747470733a2f2f7873737472696b652e746b2f696d616765732f322e706e67.png)

![ss3](https://image.ibb.co/cwjqa8/68747470733a2f2f7873737472696b652e746b2f696d616765732f342e706e67.png)

![ss4](https://image.ibb.co/gmf7No/68747470733a2f2f7873737472696b652e746b2f696d616765732f352e706e67.png)

#### License
XSStrike is licensed under MIT license.
