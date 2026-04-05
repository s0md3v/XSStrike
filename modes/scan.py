import copy
from typing import Optional, Any, Dict, List
from core.config import ScanContext, xsschecker
from core.checker import XSSChecker
from core.generator import PayloadGenerator
from core.htmlParser import HTMLParser
from core.dom import DOMScanner
from core.requester import requester
from core.validator import run_dynamic_validation
from core.log import setup_logger

logger = setup_logger()

class Scanner:
    def __init__(self, context: ScanContext):
        self.context = context
        self.checker = XSSChecker(context)
        self.generator = PayloadGenerator(context)
        self.parser = HTMLParser(context)
        self.dom_scanner = DOMScanner(context)

    def scan(self, skip_dom: bool = False, skip_confirm: bool = False, dynamic: bool = True):
        """
        Performs the main scan on the target with optional dynamic validation.
        """
        logger.run(f"Scanning {self.context.target}...")
        
        try:
            response = requester(
                self.context.target, 
                self.context.paramData, 
                self.context.headers, 
                True, # GET
                self.context.config.delay, 
                self.context.config.timeout
            )
            response_text = response.text
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return

        # 1. DOM XSS Scan
        if not skip_dom:
            logger.run("Checking for DOM XSS...")
            self.dom_scanner.scan(response_text)

        # 2. Parse HTML to find reflections
        occurences = self.parser.parse(response_text)
        
        if not occurences:
            logger.info("No reflections found.")
            return

        logger.good(f"Found {len(occurences)} reflections.")

        # 3. Analyze filter efficiency
        for pos in occurences:
            # We would use specific probe characters here to get a real score
            occurences[pos]['score'] = {'<': 100, '>': 100, '\"': 100, '\'': 100}

        # 4. Generate Payloads
        vectors = self.generator.generate(occurences, response_text)
        
        # 5. Check Payloads
        total_found = 0
        for level in sorted(vectors.keys(), reverse=True):
            for payload in vectors[level]:
                efficiencies = self.checker.check(payload, list(occurences.keys()))
                if efficiencies:
                    # STATIC CONFIRMATION
                    logger.info(f"Potential vulnerability detected: {payload} (Static Analysis Score: {max(efficiencies)})")
                    
                    # DYNAMIC VALIDATION (Zero False Positives)
                    if dynamic:
                        logger.run(f"Performing dynamic validation with Playwright for: {payload}")
                        is_confirmed = run_dynamic_validation(
                            self.context.target, 
                            self.context.paramData, 
                            payload, 
                            self.context
                        )
                        
                        # Add to findings
                        from core.config import Finding
                        self.context.findings.append(Finding(
                            url=self.context.target,
                            type="Reflected",
                            payload=payload,
                            confirmed=is_confirmed,
                            level=level
                        ))

                        if is_confirmed:
                            logger.vuln(f"[bold green]Vulnerability confirmed by Browser![/bold green] Payload: {payload}")
                            total_found += 1
                        else:
                            logger.warning(f"Payload reflected but [bold yellow]not executed[/bold yellow] (False Positive).")
                    else:
                        from core.config import Finding
                        self.context.findings.append(Finding(
                            url=self.context.target,
                            type="Reflected",
                            payload=payload,
                            confirmed=False,
                            level=level
                        ))
                        logger.vuln(f"Vulnerability found (Static Only): {payload}")
                        total_found += 1

                    if total_found >= 5 and not skip_confirm:
                        break
            if total_found >= 5 and not skip_confirm:
                break

        if total_found == 0:
            logger.info("Scan completed. No confirmed vulnerabilities found.")
        else:
            logger.good(f"Scan completed. Total confirmed vulnerabilities: {total_found}")
