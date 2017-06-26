# XSStrike
XSStrike is a python which can fuzz and bruteforce parameters for XSS. It can also detect and bypass WAFs.
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
## Using XSStrike

![XSStrike 1]( http://teamultimate.in/wp-content/uploads/2017/06/Screenshot-from-2017-06-26-15-12-19.png "Screenshot")

You can enter your target URL now but remember, you have to mark the most crucial parameter by inserting "d3v<" in it.

For example: target.com/search.php?q=d3v&category=1

After you enter your target URL, XSStrike will check if the target is protected by a WAF or not.
If its not protected by WAF you will get three options

1. Fuzzer: It checks how the input gets reflected in the webpage and then tries to build a payload according to that.
![XSStrike 2]( http://teamultimate.in/wp-content/uploads/2017/06/Screenshot-from-2017-06-26-15-14-29.png "Screenshot 2")

2. Striker: It bruteforces all the parameters one by one and generates the proof of concept in a browser window.
![XSStrike 3]( http://teamultimate.in/wp-content/uploads/2017/06/Screenshot-from-2017-06-26-15-15-24.png "Screenshot 3")

3. Hulk: Hulk uses a different approach, it doesn't care about reflection of input. It has a list of polyglots and solid payloads, it just enters them one by one in the target parameter and opens the resulted URL in a browser window.

![XSStrike 4]( http://teamultimate.in/wp-content/uploads/2017/06/Screenshot-from-2017-06-26-15-16-36.png "Screenshot 4")

XSStrike can also bypass WAFs
![XSStrike 5]( http://teamultimate.in/wp-content/uploads/2017/06/Screenshot-from-2017-06-26-15-17-29.png "Screenshot 5")

XSStrike currently supports GET only but support for POST will be added soon. Unlike other stupid bruteforce programs, XSStrike has a small list of payloads but they are the best one. Most of them are carefully crafted by me.

If you find any bug or have any suggestion to make the program better please let me know on Ultimate Hacker's [facebook page](https://www.facebook.com/weareultimates) or start an issue on XSStrike's Github repository.

### Credits
XSStrike is inspired from [BruteXSS](https://github.com/shawarkhanethicalhacker/BruteXSS) and [Intellifuzz-XSS](https://github.com/matthewdfuller/intellifuzzer-xss).
