**Note:** Changes before version 2.0.0 (pre-beta) aren't mentioned and the semantic version naming schema will be followed after a stable release.

#### v2.0.0 (Beta)
- Replaced `alert` with `confirm` in all payloads & functions
- Added new payloads for HULK
- Added detection of GET & POST parameters
- Fixed filter checker
- Fixed some bugs in injector
- Fixed a major bug in WAF detector
- Fixed a bug in parameter finder
- Fixed a bug that generated invalid payloads
- Fixed a bug that caused HULK to inject the same payload everytime
- Added handmade HTML parser
- Fixed JS context injector
- Removed Python 2 support & added Python 3 support
- Added detection of new WAFs `Wordfence, Comodo, Sucuri, CodeIgniter, Cloudflare, Barracuda, AkamaiGhost`
- Tried to implement a modular design
- Improvements in WAF Handling
- Temporarily removed HULK
- Refactored `initiator` function for better performance
- Removed `%0c` from fillings list
- Added cookies support
- Better fuzz strings for fuzzing WAFs
- Added detection of `nginx` WAF
- Minor fixes
- Fixed a bug which caused XSStrike to crash after supplying a cookie to url with no params & GET method
- Fixed Regex in `paramfinder` module

#### v2.0.0 (Pre-Beta)
- Intitial Release
- Resolved a bug that caused XSStrike to terminate in case of an active WAF
- Fixed cookie handling
