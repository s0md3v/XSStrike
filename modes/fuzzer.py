import copy
import time
from typing import Dict, Any, List
from core.config import ScanContext, fuzzes, xsschecker
from core.requester import Requester
from core.utils import replaceValue
from core.log import setup_logger

logger = setup_logger()

class XSSFuzzer:
    def __init__(self, context: ScanContext):
        self.context = context
        self.requester = Requester(context)

    def fuzz(self):
        """
        Fuzzes the target parameters with various strings to identify WAF behavior.
        """
        logger.run(f"Starting Fuzzer on {self.context.target}")
        
        # Test each fuzz string
        for fuzz in fuzzes:
            try:
                # Prepare data with fuzz string
                data = replaceValue(
                    self.context.paramData, 
                    self.context.config.xsschecker, 
                    fuzz, 
                    copy.deepcopy
                )
                
                response = self.requester.request(self.context.target, data=data)
                
                # Analyze efficiency of reflection (simplified for fuzzer)
                if fuzz in response.text:
                    logger.good(f"Fuzz string [bold green]reflected[/bold green]: {fuzz}")
                else:
                    logger.warning(f"Fuzz string [bold red]filtered[/bold red]: {fuzz}")
                
            except Exception as e:
                logger.error(f"Fuzz string blocked or request failed: {fuzz} ({e})")
                # Handle potential IP blocking or rate limiting
                if self.context.config.delay == 0:
                    logger.info("Consider using a delay (--delay) to avoid WAF blocking.")
                
                # Wait a bit before retrying if a block is suspected
                time.sleep(self.context.config.delay + 5)
        
        logger.good("Fuzzing completed.")
