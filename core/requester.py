import requests
import time
import random
import urllib3
from typing import Dict, Any, Optional, Union
from core.config import ScanContext

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Requester:
    def __init__(self, context: ScanContext):
        self.context = context
        self.session = requests.Session()
        # Apply Session Cookies
        if self.context.config.cookies:
            self.session.cookies.update(self.context.config.cookies)
        
        self.user_agents = [
            'Mozilla/5.0 (X11; Linux i686; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        ]

    def request(self, url: str, data: Any = None, method: str = "GET") -> requests.Response:
        """
        Performs an HTTP request with automatic retries and delay management.
        """
        headers = self.context.headers.copy()
        if headers.get('User-Agent') == '$':
            headers['User-Agent'] = random.choice(self.user_agents)

        # Apply global delay
        if self.context.config.delay > 0:
            time.sleep(self.context.config.delay)

        try:
            if method.upper() == "GET":
                response = self.session.get(
                    url, 
                    params=data, 
                    headers=headers, 
                    timeout=self.context.config.timeout,
                    proxies=self.context.config.proxies,
                    verify=False
                )
            else:
                # Handle JSON data automatically if configured
                is_json = headers.get('Content-type') == 'application/json'
                response = self.session.post(
                    url, 
                    json=data if is_json else None,
                    data=data if not is_json else None,
                    headers=headers, 
                    timeout=self.context.config.timeout,
                    proxies=self.context.config.proxies,
                    verify=False
                )
            
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # For XSStrike, we often want the response even if it's 403 (WAF)
            if hasattr(e, 'response') and e.response is not None:
                return e.response
            raise e

# Legacy function wrapper for compatibility during migration
def requester(url, data, headers, GET, delay, timeout):
    from core.config import XSSConfig
    config = XSSConfig(delay=delay, timeout=timeout)
    context = ScanContext(config=config, headers=headers)
    r = Requester(context)
    return r.request(url, data, method="GET" if GET else "POST")
