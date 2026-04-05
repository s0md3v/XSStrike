import json
import random
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import Dict, Any, List, Optional, Union, Tuple, Set

# Local imports
import core.config
from core.config import XSSConfig

def find_db_file(filename: str) -> Optional[Path]:
    """
    Finds a file in the db directory, supporting both direct execution and package installation.
    """
    utils_path = Path(__file__).parent
    
    potential_paths = [
        utils_path.parent / 'db' / filename,
        Path(sys.path[0]) / 'db' / filename if sys.path else None,
        utils_path.parent.parent / 'db' / filename,
        Path.cwd() / 'db' / filename,
    ]
    
    # Check all potential paths
    for p in filter(None, potential_paths):
        if p.exists():
            return p
            
    # Fallback to searching in sys.path
    for path in sys.path:
        p1 = Path(path) / 'db' / filename
        if p1.exists(): return p1
        p2 = Path(path) / 'xsstrike' / 'db' / filename
        if p2.exists(): return p2
        
    return None

def extract_headers(headers_str: str) -> Dict[str, str]:
    """Parses a string of headers into a dictionary."""
    headers_str = headers_str.replace('\\n', '\n')
    headers_dict = {}
    matches = re.findall(r'([^:\n]+):\s*([^\n]+)', headers_str)
    for key, value in matches:
        headers_dict[key.strip()] = value.strip().rstrip(',')
    return headers_dict

def extract_cookies(cookie_str: str) -> Dict[str, str]:
    """Parses a raw cookie string into a dictionary."""
    cookies = {}
    for part in cookie_str.split(';'):
        if '=' in part:
            k, v = part.strip().split('=', 1)
            cookies[k] = v
    return cookies

def replace_value(mapping: Any, old: Any, new: Any, strategy: Optional[Any] = None) -> Any:
    """
    Replaces old values with new ones in a dictionary or list, optionally using a copy strategy.
    """
    result = strategy(mapping) if strategy else mapping
    
    if isinstance(result, dict):
        for k, v in result.items():
            if v == old:
                result[k] = new
            elif isinstance(v, (dict, list)):
                result[k] = replace_value(v, old, new)
    elif isinstance(result, list):
        for i, v in enumerate(result):
            if v == old:
                result[i] = new
            elif isinstance(v, (dict, list)):
                result[i] = replace_value(v, old, new)
                
    return result

def extract_scripts(response_text: str, checker: str = 'v3dm0s') -> List[str]:
    """Extracts script contents that contain the checker string."""
    scripts = []
    # Using a more robust regex for script extraction
    matches = re.findall(r'(?si)<script.*?>\s*(.*?)\s*</script>', response_text)
    for script_content in matches:
        if checker in script_content:
            scripts.append(script_content)
    return scripts

def random_upper(string: str) -> str:
    """Randomly converts characters of a string to uppercase for WAF evasion."""
    return ''.join(random.choice((c.upper(), c.lower())) for c in string)

def reader(path: Union[str, Path]) -> List[str]:
    """Reads a file and returns a list of lines, decoded as UTF-8."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f]
    except (UnicodeDecodeError, IOError):
        # Fallback for different encodings if needed
        with open(path, 'r', encoding='latin-1') as f:
            return [line.rstrip('\n') for line in f]

def fill_holes(original: List[int], new: List[int]) -> List[int]:
    """Aligne reflections found in the response with their original positions."""
    filler = 0
    filled = []
    for x, y in zip(original, new):
        if int(x) == (y + filler):
            filled.append(y)
        else:
            filled.extend([0, y])
            filler += (int(x) - y)
    return filled

def gen_gen(fillings: Tuple[str, ...], e_fillings: Tuple[str, ...], l_fillings: Tuple[str, ...], 
           event_handlers: Dict[str, List[str]], tags: Tuple[str, ...], 
           functions: Tuple[str, ...], ends: List[str], bad_tag: Optional[str] = None) -> List[str]:
    """Generates XSS vectors based on various permutations."""
    vectors = []
    r = random_upper
    checker = core.config.xsschecker # Legacy fallback
    
    for tag in tags:
        bait = checker if tag in ('d3v', 'a') else ''
        for handler, compatible_tags in event_handlers.items():
            if tag in compatible_tags:
                for func in functions:
                    for fill in fillings:
                        for e_fill in e_fillings:
                            for l_fill in l_fillings:
                                for end in ends:
                                    if tag in ('d3v', 'a') and '>' in ends:
                                        end = '>'
                                    breaker = f'</{r(bad_tag)}>' if bad_tag else ''
                                    vector = f"{breaker}<{r(tag)}{fill}{r(handler)}{e_fill}={e_fill}{func}{l_fill}{end}{bait}"
                                    vectors.append(vector)
    return vectors

def get_url(url: str, get_method: bool) -> str:
    """Returns the base URL for GET requests."""
    return url.split('?')[0] if get_method else url

def get_params(url: str, data: Any, get_method: bool) -> Optional[Dict[str, str]]:
    """Extracts parameters from URL or POST data."""
    params = {}
    if get_method and '?' in url:
        query = urlparse(url).query
        params = dict(part.split('=', 1) if '=' in part else (part, '') for part in query.split('&'))
    elif data:
        if isinstance(data, dict):
            return data
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            # Parse as form-data
            params = dict(part.split('=', 1) if '=' in part else (part, '') for part in str(data).split('&'))
    return params

def handle_anchor(parent_url: str, url: str) -> str:
    """Joins a base URL with a relative URL."""
    return urljoin(parent_url, url)

def stripper(string, substring, direction='right'):
    done = False
    strippedString = ''
    if direction == 'right':
        string = string[::-1]
    for char in string:
        if char == substring and not done:
            done = True
        else:
            strippedString += char
    if direction == 'right':
        strippedString = strippedString[::-1]
    return strippedString

# Legacy aliases for compatibility
extractHeaders = extract_headers
replaceValue = replace_value
extractScripts = extract_scripts
randomUpper = random_upper
genGen = gen_gen
fillHoles = fill_holes
getUrl = get_url
getParams = get_params
converter = lambda data, url=False: json.dumps(data) if not isinstance(data, str) else json.loads(data)
