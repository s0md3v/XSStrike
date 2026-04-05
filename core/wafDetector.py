import re
import json
from typing import Optional, Dict, Any
from core.requester import Requester
from core.config import ScanContext, fuzzes
from core.utils import find_db_file
from core.log import setup_logger

logger = setup_logger()

class WAFDetector:
    def __init__(self, context: ScanContext):
        self.context = context
        self.requester = Requester(context)
        self.signatures: Dict[str, Any] = {}
        self._load_signatures()

    def _load_signatures(self):
        """Loads WAF signatures from JSON database."""
        sig_file = find_db_file('wafSignatures.json')
        if sig_file:
            with open(sig_file, 'r') as f:
                self.signatures = json.load(f)

    def detect(self) -> Optional[str]:
        """
        Sends various fuzz strings to detect WAF presence and type.
        """
        logger.run("Checking for WAF presence...")
        
        # Test each fuzz string until a WAF is detected
        for fuzz in fuzzes:
            try:
                # We need to test where the payload is injected (params or path)
                params = self.context.paramData or {"xss": fuzz}
                if isinstance(params, dict):
                    params["xss"] = fuzz
                
                response = self.requester.request(self.context.target, data=params)
                
                # Analyze response for WAF signatures
                waf_name = self._analyze_response(response)
                if waf_name:
                    logger.warning(f"WAF detected: [bold red]{waf_name}[/bold red]")
                    return waf_name
                
            except Exception:
                # If request times out or is dropped, it's a strong indicator of WAF
                logger.warning("Request timed out or dropped. Possible generic WAF/IDS active.")
                return "Generic WAF/IDS"
                
        logger.info("No WAF detected.")
        return None

    def _analyze_response(self, response) -> Optional[str]:
        """Analyzes headers and body for known WAF signatures."""
        for name, sig in self.signatures.items():
            # Check headers
            if 'headers' in sig:
                for header, pattern in sig['headers'].items():
                    if header in response.headers:
                        if re.search(pattern, response.headers[header], re.IGNORECASE):
                            return name
            
            # Check body/reason
            if 'page' in sig:
                if re.search(sig['page'], response.text, re.IGNORECASE):
                    return name
            
            # Check status code
            if 'code' in sig:
                if response.status_code == sig['code']:
                    return name
        return None
