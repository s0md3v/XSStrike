import concurrent.futures
import uuid
from urllib.parse import urlparse
from typing import List, Set, Dict, Any, Tuple
from core.config import ScanContext, blindPayload
from core.photon import PhotonCrawler
from modes.scan import Scanner
from core.log import setup_logger
from core.requester import Requester

logger = setup_logger()

class XSScrawler:
    def __init__(self, context: ScanContext):
        self.context = context
        self.crawler = PhotonCrawler(context)
        self.requester = Requester(context)
        self.stored_payloads: List[Tuple[str, Dict[str, Any], str]] = [] # (url, params, id)

    def run(self, level: int = 2, stored: bool = True):
        """
        Runs the crawling process, scans for Reflected XSS, and performs Stored XSS checks.
        """
        target = self.context.target
        if not target:
            logger.error("No target specified for crawler.")
            return

        # 1. Start Crawling
        forms, urls = self.crawler.crawl(target, depth=level)
        
        # 2. Reflected XSS Scan (Current logic)
        self._scan_reflected(forms, urls)
        
        # 3. Stored XSS Injections
        if stored:
            logger.run("Starting Stored XSS injection phase...")
            self._inject_stored_payloads(forms)
            
            # 4. Stored XSS Verification (Re-visit all URLs)
            logger.run("Starting Stored XSS verification phase (re-visiting all pages)...")
            self._verify_stored_xss(urls)

    def _scan_reflected(self, forms, urls):
        """Standard concurrent scan for reflected XSS."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.context.config.threadCount) as executor:
            futures = []
            for form in forms:
                form_context = self.context.model_copy()
                form_context.target = self._get_full_url(form['action'])
                scanner = Scanner(form_context)
                futures.append(executor.submit(scanner.scan, skip_confirm=True))
            
            for url in urls:
                url_context = self.context.model_copy()
                url_context.target = url
                scanner = Scanner(url_context)
                futures.append(executor.submit(scanner.scan, skip_confirm=True))

    def _inject_stored_payloads(self, forms):
        """Injects unique payloads into every input field of every form found."""
        for form in forms:
            action_url = self._get_full_url(form['action'])
            method = form.get('method', 'POST')
            inputs = form.get('inputs', [])
            
            # Prepare params: inject the same unique ID in all fields of this form submission
            unique_id = f"v3dm0s_stored_{uuid.uuid4().hex[:6]}"
            params = {name: unique_id for name in inputs}
            
            try:
                self.requester.request(action_url, data=params, method=method)
                self.stored_payloads.append((action_url, params, unique_id))
                logger.info(f"Injected stored payload [bold blue]{unique_id}[/bold blue] into {len(inputs)} fields at {action_url}")
            except Exception as e:
                logger.debug(f"Stored injection failed at {action_url}: {e}")

    def _verify_stored_xss(self, urls):
        """Re-visits every URL to see if any stored payload is reflected and executable."""
        for url in urls:
            try:
                response = self.requester.request(url)
                for inj_url, params, unique_id in self.stored_payloads:
                    if unique_id in response.text:
                        logger.vuln(f"[bold red]Stored XSS Reflection Found![/bold red] Injected at {inj_url}, Triggered at {url}")
                        # Dynamic confirmation for Stored XSS
                        from core.validator import run_dynamic_validation
                        is_confirmed = run_dynamic_validation(url, {}, unique_id, self.context)
                        
                        # Add to findings
                        from core.config import Finding
                        self.context.findings.append(Finding(
                            url=url,
                            type="Stored",
                            payload=unique_id,
                            parameter="Form Injection",
                            confirmed=is_confirmed,
                            level=10
                        ))

                        if is_confirmed:
                            logger.vuln(f"[bold green]STORED XSS CONFIRMED BY BROWSER![/bold green] (Injected: {inj_url} | Triggered: {url})")
            except Exception as e:
                logger.debug(f"Verification visit failed for {url}: {e}")

    def _get_full_url(self, action: str) -> str:
        if action.startswith('http'):
            return action
        parsed = urlparse(self.context.target)
        return f"{parsed.scheme}://{parsed.netloc}{action if action.startswith('/') else '/' + action}"
