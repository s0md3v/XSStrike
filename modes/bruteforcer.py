import copy
from urllib.parse import urlparse, unquote
from typing import List, Optional, Any

from core.requester import Requester
from core.utils import get_url, get_params
from core.config import ScanContext
from core.log import setup_logger

logger = setup_logger()

class XSSBruteforcer:
    def __init__(self, context: ScanContext):
        self.context = context
        self.requester = Requester(context)

    def run(self, payload_list: List[str]):
        """
        Bruteforces parameters using a provided list of payloads.
        """
        target = self.context.target
        if not target:
            logger.error("No target specified for bruteforcer.")
            return

        is_get = not self.context.paramData
        url = get_url(target, is_get)
        params = get_params(target, self.context.paramData, is_get)
        
        if not params:
            logger.error("No parameters found to bruteforce.")
            return

        logger.run(f"Starting bruteforce on {target} with {len(payload_list)} payloads.")
        
        for param_name in params.keys():
            logger.info(f"Bruteforcing parameter: [bold cyan]{param_name}[/bold cyan]")
            
            for i, payload in enumerate(payload_list, 1):
                if i % 10 == 0 or i == len(payload_list):
                    logger.debug(f"Progress for {param_name}: {i}/{len(payload_list)}")
                
                current_payload = payload
                if self.context.encoding:
                    current_payload = self.context.encoding(unquote(payload))
                
                # Prepare params with payload
                current_params = copy.deepcopy(params)
                current_params[param_name] = current_payload
                
                try:
                    response = self.requester.request(url, data=current_params, method="GET" if is_get else "POST")
                    
                    if current_payload in response.text:
                        logger.vuln(f"Payload reflected! Parameter: {param_name}, Payload: {payload}")
                except Exception as e:
                    logger.error(f"Request failed for payload {payload}: {e}")

        logger.good("Bruteforce completed.")

# Legacy wrapper
def bruteforcer(target, paramData, payloadList, encoding, headers, delay, timeout):
    from core.config import XSSConfig
    config = XSSConfig(delay=delay, timeout=timeout)
    context = ScanContext(config=config, target=target, paramData=paramData, headers=headers, encoding=encoding)
    engine = XSSBruteforcer(context)
    engine.run(payloadList)
